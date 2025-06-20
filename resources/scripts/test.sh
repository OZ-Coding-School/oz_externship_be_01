set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_BLUE=`tput setaf 4;`
COLOR_NC=`tput sgr0;` # No Color

export DJANGO_SETTINGS_MODULE=config.settings.local

cd "$(dirname "$0")/../.."

export DJANGO_SETTINGS_MODULE="config.settings.local"
echo "${COLOR_BLUE}Starting mypy${COLOR_NC}"
poetry run dmypy run -- .
echo "OK"

echo "${COLOR_BLUE}Starting Django Test with coverage${COLOR_NC}"
poetry run coverage run manage.py tests
poetry run coverage report -m
poetry run coverage html

echo "${COLOR_GREEN}Successfully Run Mypy and Test!!"
