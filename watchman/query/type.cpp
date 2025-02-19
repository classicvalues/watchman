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

#include "watchman/Errors.h"
#include "watchman/watchman_query.h"

#include <memory>

using namespace watchman;

class TypeExpr : public QueryExpr {
  char arg;

 public:
  explicit TypeExpr(char arg) : arg(arg) {}

  EvaluateResult evaluate(QueryContext*, FileResult* file) override {
    auto optionalDtype = file->dtype();
    if (!optionalDtype.has_value()) {
      return folly::none;
    }
    auto dtype = *optionalDtype;
    if (dtype != DType::Unknown) {
      switch (arg) {
        case 'b':
          return dtype == DType::Block;
        case 'c':
          return dtype == DType::Char;
        case 'p':
          return dtype == DType::Fifo;
        case 's':
          return dtype == DType::Socket;
        case 'd':
          return dtype == DType::Dir;
        case 'f':
          return dtype == DType::Regular;
        case 'l':
          return dtype == DType::Symlink;
      }
    }

    auto stat = file->stat();
    if (!stat.has_value()) {
      return folly::none;
    }

    switch (arg) {
#ifndef _WIN32
      case 'b':
        return S_ISBLK(stat->mode);
      case 'c':
        return S_ISCHR(stat->mode);
      case 'p':
        return S_ISFIFO(stat->mode);
      case 's':
        return S_ISSOCK(stat->mode);
#endif
      case 'd':
        return stat->isDir();
      case 'f':
        return stat->isFile();
      case 'l':
        return stat->isSymlink();
#ifdef S_ISDOOR
      case 'D':
        return S_ISDOOR(stat->mode);
#endif
      default:
        return false;
    }
  }

  static std::unique_ptr<QueryExpr> parse(w_query*, const json_ref& term) {
    const char *typestr, *found;
    char arg;

    if (!term.isArray()) {
      throw QueryParseError("\"type\" term requires a type string parameter");
    }

    if (term.array().size() > 1 && term.at(1).isString()) {
      typestr = json_string_value(term.at(1));
    } else {
      throw QueryParseError(folly::to<std::string>(
          "First parameter to \"type\" term must be a type string"));
    }

    found = strpbrk(typestr, "bcdfplsD");
    if (!found || strlen(typestr) > 1) {
      throw QueryParseError("invalid type string '", typestr, "'");
    }

    arg = *found;

    return std::make_unique<TypeExpr>(arg);
  }
};
W_TERM_PARSER("type", TypeExpr::parse)

/* vim:ts=2:sw=2:et:
 */
