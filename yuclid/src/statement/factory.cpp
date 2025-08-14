/**
   Copyright 2025 Concordance Inc. dba Harmonic

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
#include "factory.hpp"
#include "../point.hpp"
#include "../util.hpp"

namespace Yuclid {
  bool statement_factory::register_generator(const std::string &name, constructor gen) {
    return registry().insert({name, gen}).second;
  }

  std::unique_ptr<Statement> statement_factory::generate(const statement_data &data) const {
    auto &reg = registry();
    auto it = reg.find(data.name);
    if (it == reg.end()) {
      throw std::runtime_error("Unknown statement" + string_to_string(data.name));
    }
    return it->second(data.args)->normalize();
  }
  
}
