#pragma once

#include <filesystem>
#include <iostream>
#include <system_error>
#include <vector>

#if defined(_WIN32)
#include <windows.h>
#include <restartmanager.h>
#endif

namespace reuse_archive {
#if defined(_WIN32)
inline void ReportDeleteAccess(const std::filesystem::path& path) {
  const auto handle =
      CreateFileW(path.c_str(), DELETE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                  nullptr, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, nullptr);
  if (handle == INVALID_HANDLE_VALUE) {
    const auto error = GetLastError();
    std::cerr << "archive_delete_access path=" << path.generic_string() << " win32_error=" << error
              << '\n';
  } else {
    CloseHandle(handle);
  }
}

inline void ReportOwners(const std::vector<std::filesystem::path>& files) {
  DWORD session = 0;
  WCHAR key[CCH_RM_SESSION_KEY + 1]{};
  auto status = RmStartSession(&session, 0, key);
  std::cerr << "archive_owner_query stage=start status=" << status << '\n';
  if (status != ERROR_SUCCESS)
    return;
  struct Session {
    DWORD id;
    ~Session() { RmEndSession(id); }
  } guard{session};
  std::vector<LPCWSTR> names;
  for (const auto& file : files)
    names.push_back(file.c_str());
  status = RmRegisterResources(session, static_cast<UINT>(names.size()), names.data(), 0, nullptr,
                               0, nullptr);
  std::cerr << "archive_owner_query stage=register status=" << status << " files=" << names.size()
            << '\n';
  if (status != ERROR_SUCCESS)
    return;
  UINT needed = 0, count = 0;
  DWORD reasons = 0;
  status = RmGetList(session, &needed, &count, nullptr, &reasons);
  std::cerr << "archive_owner_query stage=size status=" << status << " needed=" << needed
            << " reasons=" << reasons << '\n';
  if (status != ERROR_MORE_DATA || needed == 0)
    return;
  std::vector<RM_PROCESS_INFO> processes(needed);
  count = needed;
  status = RmGetList(session, &needed, &count, processes.data(), &reasons);
  std::cerr << "archive_owner_query stage=list status=" << status << " count=" << count
            << " reasons=" << reasons << '\n';
  if (status != ERROR_SUCCESS)
    return;
  for (UINT index = 0; index < count; ++index) {
    const auto& process = processes[index];
    std::cerr << "archive_owner pid=" << process.Process.dwProcessId
              << " self=" << (process.Process.dwProcessId == GetCurrentProcessId())
              << " type=" << static_cast<int>(process.ApplicationType)
              << " start_high=" << process.Process.ProcessStartTime.dwHighDateTime
              << " start_low=" << process.Process.ProcessStartTime.dwLowDateTime << '\n';
  }
}
#endif

// Archive once. Diagnostic collection never retries, renames, deletes or closes foreign handles.
inline bool Rename(const std::filesystem::path& source, const std::filesystem::path& target) {
  std::error_code error;
#if defined(_WIN32)
  SetLastError(ERROR_SUCCESS);
#endif
  std::filesystem::rename(source, target, error);
#if defined(_WIN32)
  const auto last_error = GetLastError();
#endif
  if (!error) {
    std::cerr << "archive_result status=completed source=" << source.generic_string()
              << " target=" << target.generic_string() << '\n';
    return true;
  }
  std::cerr << "archive_result status=failed code=" << error.value()
            << " category=" << error.category().name();
#if defined(_WIN32)
  std::cerr << " last_win32_error=" << last_error << " pid=" << GetCurrentProcessId();
#endif
  std::cerr << " source=" << source.generic_string() << " target=" << target.generic_string()
            << " message=" << error.message() << '\n';
#if defined(_WIN32)
  ReportDeleteAccess(source);
  std::vector<std::filesystem::path> files;
  std::error_code inventory_error;
  {
    std::filesystem::directory_iterator cursor(source, inventory_error), end;
    while (!inventory_error && cursor != end) {
      if (cursor->is_regular_file(inventory_error)) {
        files.push_back(cursor->path());
        ReportDeleteAccess(files.back());
      }
      cursor.increment(inventory_error);
    }
  }
  std::cerr << "archive_inventory status=" << inventory_error.value() << " files=" << files.size()
            << '\n';
  ReportOwners(files);
#endif
  return false;
}
} // namespace reuse_archive
