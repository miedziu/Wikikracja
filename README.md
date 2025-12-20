## Wikikracja
This is community building system. Currently it consist following modules:
- voting
- citizens
- chat
- eLibrary
- board
- bookkeeping
  
Voting module (glosowania) uses principle known as Zero Knowledge Proof.
It means that voting is anonymous.

## Demo
You can check demo here:
https://demo.wikikracja.pl/

## Requirements
You will need an email account (SMTP) to send emails to users.

## Development
To run development instance:
- enable python virtualenv
- run `./scripts/dev_start.sh`

## Docker image (build & push)

### Prerequisites
- `docker login registry.gitlab.com`

### Build and push
- Push to your own namespace:
  - `REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh`
- Maintainers only (official image):
  - `CONFIRM_OFFICIAL_PUSH=1 ./scripts/build_and_push_docker_image.sh`

### Optional variables
- **Custom tag**:
  - `TAG=v1.2.3 REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh`
- **Do not push `latest`**:
  - `PUSH_LATEST=0 REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh`
- **Override the image name**:
  - `REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh`
