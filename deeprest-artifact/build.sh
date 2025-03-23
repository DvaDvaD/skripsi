# APIS
docker build -t dr-blog -f apis/blog/Dockerfile --network host .
docker build -t dr-features-service -f apis/features-service/Dockerfile --network host .
docker build -t dr-genome-nexus -f apis/genome-nexus/Dockerfile --network host .
docker build -t dr-languagetool -f apis/languagetool/Dockerfile --network host .
docker build -t dr-market -f apis/market/Dockerfile --network host .
docker build -t dr-ncs -f apis/ncs/Dockerfile --network host .
docker build -t dr-person-controller -f apis/person-controller/Dockerfile --network host .
docker build -t dr-project-tracking-system -f apis/project-tracking-system/Dockerfile --network host .
docker build -t dr-restcountries -f apis/restcountries/Dockerfile --network host .
docker build -t dr-scs -f apis/scs/Dockerfile --network host .
docker build -t dr-user-management -f apis/user-management/Dockerfile --network host .


# TOOLS
docker build -t dr-arat-rl -f tools/arat-rl/Dockerfile --network host .
docker build -t dr-deeprest -f tools/deeprest/Dockerfile --network host .
docker build -t dr-morest -f tools/morest/Dockerfile --network host .
docker build -t dr-restler -f tools/restler/Dockerfile --network host .
docker build -t dr-resttestgen -f tools/resttestgen/Dockerfile --network host .
docker build -t dr-schemathesis -f tools/schemathesis/Dockerfile --network host .
