cd /RESTler/restler
./Restler compile --api_spec /specifications/$API-openapi.json
while true; do ./Restler fuzz --grammar_file ./Compile/grammar.py --dictionary_file ./Compile/dict.json --settings ./Compile/engine_settings.json --no_ssl --target_port $PORT --time_budget 2; done