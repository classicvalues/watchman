/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once

#include <folly/Conv.h>
#include <folly/Range.h>
#include <stdexcept>

#include "watchman/watchman_preprocessor.h"

class json_ref;
struct watchman_client;

namespace watchman {
using command_func = void (*)(watchman_client* client, const json_ref& args);

// Should throw an exception (ideally CommandValidationError) if validation
// fails
using cli_cmd_validate_func = void (*)(json_ref& args);

using command_flags = int;
constexpr int CMD_DAEMON = 1;
constexpr int CMD_CLIENT = 2;
constexpr int CMD_POISON_IMMUNE = 4;
constexpr int CMD_ALLOW_ANY_USER = 8;

struct command_handler_def {
  const char* name;
  command_func func;
  command_flags flags;
  cli_cmd_validate_func cli_validate;
};

class CommandValidationError : public std::runtime_error {
 public:
  template <typename... Args>
  explicit CommandValidationError(Args&&... args)
      : std::runtime_error(folly::to<std::string>(
            "failed to validate command: ",
            std::forward<Args>(args)...)) {}
};

void register_command(command_handler_def& defs);

/**
 * Provide a way to query (and eventually modify) command line arguments
 *
 * This is not thread-safe and should only be invoked from main()
 */
command_handler_def* lookup_command(folly::StringPiece cmd_name, int mode);

std::vector<command_handler_def*> get_all_commands();

#define W_CMD_REG_1(symbol, name, func, flags, clivalidate) \
  static w_ctor_fn_type(symbol) {                           \
    static ::watchman::command_handler_def d = {            \
        name, func, flags, clivalidate};                    \
    ::watchman::register_command(d);                        \
  }                                                         \
  w_ctor_fn_reg(symbol)

#define W_CMD_REG(name, func, flags, clivalidate) \
  W_CMD_REG_1(w_gen_symbol(w_cmd_register_), name, func, flags, clivalidate)

#define W_CAP_REG1(symbol, name)           \
  static w_ctor_fn_type(symbol) {          \
    ::watchman::capability_register(name); \
  }                                        \
  w_ctor_fn_reg(symbol)

#define W_CAP_REG(name) W_CAP_REG1(w_gen_symbol(w_cap_reg_), name)

void capability_register(const char* name);
bool capability_supported(folly::StringPiece name);
json_ref capability_get_list();

} // namespace watchman

/* vim:ts=2:sw=2:et:
 */
