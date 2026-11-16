# Thin wrapper: every target calls the workspace's gamekit on this game.
# The tools live in ../../tools/gamekit (see its README). `make help` lists targets.

GAMEKIT ?= ../../tools/gamekit/bin/gamekit
CHAR    ?=

.PHONY: help run edit test shot sprites sample-sprite preview export export-linux export-windows export-web smoke-web clean

help: ## List the commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-16s %s\n", $$1, $$2}'

run: ## Play the game
	$(GAMEKIT) run .
edit: ## Open the Godot editor
	$(GAMEKIT) edit .
test: ## Unit + integration tests
	$(GAMEKIT) test .
shot: ## Run windowed and save the last frame to builds/shots/
	$(GAMEKIT) shot .
sprites: ## LPC exports in assets/source/lpc -> SpriteFrames + credits
	$(GAMEKIT) sprites .
sample-sprite: ## Compose a sample LPC character offline
	$(GAMEKIT) sample-sprite .
preview: ## Character viewer (CHAR=<name>)
	$(GAMEKIT) preview . $(CHAR)
export: ## Test, then Linux + Windows + Web -> builds/dist/
	$(GAMEKIT) export .
export-linux: ## Linux only
	$(GAMEKIT) export . Linux
export-windows: ## Windows only
	$(GAMEKIT) export . Windows
export-web: ## Web only (zip uploads to itch.io)
	$(GAMEKIT) export . Web
smoke-web: ## Load the Web build in headless Chrome
	$(GAMEKIT) smoke-web .
clean: ## Remove build output
	rm -rf builds
