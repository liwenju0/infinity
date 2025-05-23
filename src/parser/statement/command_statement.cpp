// Copyright(C) 2023 InfiniFlow, Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "command_statement.h"

namespace infinity {

std::string UseCmd::ToString() const { return "Use Command"; }
std::string SetCmd::ToString() const { return "Set Command"; }
std::string ExportCmd::ToString() const { return "Export Command"; }
std::string CheckTable::ToString() const { return "Check Table Command"; }
std::string CommandStatement::ToString() const { return command_info_->ToString(); }
std::string CleanupCmd::ToString() const { return "Cleanup Command"; }
std::string DumpIndexCmd::ToString() const { return "Dump Index Command"; }
std::string TestCmd::ToString() const { return "Test Command: " + command_content_; }
std::string SnapshotCmd::ToString() const { return "Snapshot command"; }

} // namespace infinity