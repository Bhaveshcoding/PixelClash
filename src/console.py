from typing import Any, Dict, List, Optional, Tuple

import pygame

from constants import HEIGHT, WIDTH


class DeveloperConsole:
    """A lightweight developer console overlay for runtime commands."""

    def __init__(self, game: Any, font: Optional[pygame.font.Font] = None) -> None:
        self.game = game
        self.is_open = False
        self.current_input = ""
        self.cursor = 0
        self.history: List[str] = []
        self.history_index = -1
        self.autocomplete = ""
        self.output: List[Dict[str, str]] = []
        self.font = font or pygame.font.SysFont("arial", 18)
        self.prompt = "> "
        self.commands = [
            "/help",
            "/fps",
            "/heal",
            "/give health",
            "/give damage",
            "/give shield",
            "/spawn crate",
            "/spawn pickup",
            "/reset match",
            "/profile",
            "/history",
            "/achievements",
            "/god",
        ]
        self._add_output("INFO", "Developer console ready. Type /help for commands.")

    def toggle(self) -> None:
        """Toggle the console visibility."""
        self.is_open = not self.is_open
        if not self.is_open:
            self.autocomplete = ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event for the console."""
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_BACKQUOTE:
            self.toggle()
            return True

        if not self.is_open:
            return False

        if event.key == pygame.K_ESCAPE:
            self.is_open = False
            return True

        if event.key == pygame.K_RETURN:
            self.execute_command(self.current_input.strip())
            self.history.append(self.current_input.strip())
            self.current_input = ""
            self.cursor = 0
            self.history_index = -1
            self.autocomplete = ""
            return True

        if event.key == pygame.K_TAB:
            self.autocomplete_command()
            return True

        if event.key == pygame.K_BACKSPACE:
            self._delete_char()
            return True

        if event.key == pygame.K_UP:
            self._history_previous()
            return True

        if event.key == pygame.K_DOWN:
            self._history_next()
            return True

        if event.key == pygame.K_LEFT:
            self.cursor = max(0, self.cursor - 1)
            return True

        if event.key == pygame.K_RIGHT:
            self.cursor = min(len(self.current_input), self.cursor + 1)
            return True

        if event.key == pygame.K_HOME:
            self.cursor = 0
            return True

        if event.key == pygame.K_END:
            self.cursor = len(self.current_input)
            return True

        if event.unicode and event.unicode.isprintable():
            self._insert_char(event.unicode)
            return True

        return False

    def _insert_char(self, char: str) -> None:
        self.current_input = self.current_input[: self.cursor] + char + self.current_input[self.cursor :]
        self.cursor += 1

    def _delete_char(self) -> None:
        if self.cursor > 0:
            self.current_input = self.current_input[: self.cursor - 1] + self.current_input[self.cursor :]
            self.cursor -= 1

    def _history_previous(self) -> None:
        if not self.history:
            return
        if self.history_index < 0:
            self.history_index = len(self.history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)
        self.current_input = self.history[self.history_index]
        self.cursor = len(self.current_input)

    def _history_next(self) -> None:
        if not self.history:
            return
        if self.history_index < 0:
            return
        self.history_index += 1
        if self.history_index >= len(self.history):
            self.current_input = ""
            self.cursor = 0
            self.history_index = -1
        else:
            self.current_input = self.history[self.history_index]
            self.cursor = len(self.current_input)

    def autocomplete_command(self) -> None:
        if not self.current_input:
            return
        prefix = self.current_input.strip().lstrip("/")
        matches = [cmd for cmd in self.commands if cmd.startswith("/" + prefix)]
        if matches:
            self.current_input = matches[0]
            self.cursor = len(self.current_input)
            self.autocomplete = matches[0]

    def execute_command(self, text: str) -> None:
        if not text:
            self._add_output("WARNING", "Empty command.")
            return

        self._add_output("INFO", f"> {text}")
        parts = text.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "/help":
            self._add_output("INFO", "Commands: /help, /fps, /heal, /give health, /give damage, /give shield, /spawn crate, /spawn pickup, /reset match, /profile, /history, /achievements, /god")
            return

        if command == "/fps":
            fps = int(self.game.clock.get_fps()) if self.game and getattr(self.game, "clock", None) else 0
            self._add_output("INFO", f"FPS: {fps}")
            return

        if command == "/heal":
            self._heal_player()
            return

        if command == "/give":
            if not args:
                self._add_output("ERROR", "Usage: /give health|damage|shield")
                return
            target = args[0].lower()
            if target == "health":
                self._give_health()
            elif target == "damage":
                self._give_damage()
            elif target == "shield":
                self._give_shield()
            else:
                self._add_output("ERROR", "Unknown item. Use health, damage, or shield.")
            return

        if command == "/spawn":
            if not args:
                self._add_output("ERROR", "Usage: /spawn crate|pickup")
                return
            target = args[0].lower()
            if target == "crate":
                self._spawn_crate()
            elif target == "pickup":
                self._spawn_pickup()
            else:
                self._add_output("ERROR", "Unknown spawn target. Use crate or pickup.")
            return

        if command == "/reset":
            if args and args[0].lower() == "match":
                self._reset_match()
            else:
                self._add_output("ERROR", "Usage: /reset match")
            return

        if command == "/profile":
            self._show_profile()
            return

        if command == "/history":
            self._show_history()
            return

        if command == "/achievements":
            self._show_achievements()
            return

        if command == "/god":
            self._toggle_god()
            return

        self._add_output("ERROR", f"Unknown command: {command}")

    def _add_output(self, level: str, message: str) -> None:
        self.output.append({"level": level, "text": str(message)})
        if len(self.output) > 80:
            self.output = self.output[-80:]

    def _heal_player(self) -> None:
        state = self._active_player_state()
        if state is None:
            self._add_output("WARNING", "No active player state available.")
            return
        state["health"] = 100
        self._add_output("INFO", "Player healed.")

    def _give_health(self) -> None:
        state = self._active_player_state()
        if state is None:
            self._add_output("WARNING", "No active player state available.")
            return
        state["health"] = 100
        self._add_output("INFO", "Applied health.")

    def _give_damage(self) -> None:
        state = self._active_player_state()
        if state is None:
            self._add_output("WARNING", "No active player state available.")
            return
        state["active_buff"] = "DAMAGE"
        state["buff_timer"] = 10.0
        self._add_output("INFO", "Applied damage buff.")

    def _give_shield(self) -> None:
        state = self._active_player_state()
        if state is None:
            self._add_output("WARNING", "No active player state available.")
            return
        state["active_buff"] = "SHIELD"
        state["buff_timer"] = 10.0
        self._add_output("INFO", "Applied shield buff.")

    def _spawn_crate(self) -> None:
        if self.game is None:
            self._add_output("WARNING", "No active game instance.")
            return
        player_pos = self._player_position()
        if player_pos is None:
            self._add_output("WARNING", "No player position available.")
            return
        self.game.server_crates.append({"x": int(player_pos[0]), "y": int(player_pos[1]), "hp": 50, "id": len(self.game.server_crates)})
        self._add_output("INFO", "Spawned crate.")

    def _spawn_pickup(self) -> None:
        if self.game is None:
            self._add_output("WARNING", "No active game instance.")
            return
        player_pos = self._player_position()
        if player_pos is None:
            self._add_output("WARNING", "No player position available.")
            return
        pickup_id = max(list(self.game.server_pickups.keys()), default=-1) + 1
        self.game.server_pickups[pickup_id] = {"x": int(player_pos[0]), "y": int(player_pos[1]), "type": "HEALTH"}
        self._add_output("INFO", "Spawned health pickup.")

    def _reset_match(self) -> None:
        if self.game is None:
            self._add_output("WARNING", "No active game instance.")
            return
        self.game.winner = ""
        self.game.stats.reset_all()
        self.game.match_started_at = pygame.time.get_ticks() / 1000.0
        self.game.match_summary_logged = False
        self._add_output("INFO", "Match reset.")

    def _show_profile(self) -> None:
        if self.game and getattr(self.game, "profile", None):
            profile = self.game.profile.data
            self._add_output("INFO", f"Player: {profile.get('player_name', 'Player')}")
            self._add_output("INFO", f"Wins: {profile.get('total_wins', 0)}")
            self._add_output("INFO", f"Matches: {profile.get('total_matches', 0)}")
            self._add_output("INFO", f"Favorite Weapon: {profile.get('favorite_weapon', 'N/A')}")
        else:
            self._add_output("WARNING", "Profile manager unavailable.")

    def _show_history(self) -> None:
        if self.game and getattr(self.game, "history", None):
            matches = self.game.history.load_matches()
            if not matches:
                self._add_output("WARNING", "No match history available.")
                return
            for match in matches[:5]:
                self._add_output("INFO", f"{match.get('date', 'unknown')} -> {match.get('winner', 'none')}")
        else:
            self._add_output("WARNING", "History manager unavailable.")

    def _show_achievements(self) -> None:
        if self.game and getattr(self.game, "achievements", None):
            for name, achievement in self.game.achievements.achievements.items():
                status = "UNLOCKED" if achievement.unlocked else "LOCKED"
                self._add_output("INFO", f"{name}: {status}")
        else:
            self._add_output("WARNING", "Achievement manager unavailable.")

    def _toggle_god(self) -> None:
        self.game.console.god_mode = not getattr(self.game.console, "god_mode", False)
        self._add_output("INFO", "God mode enabled." if self.game.console.god_mode else "God mode disabled.")

    def _active_player_state(self) -> Optional[Dict[str, Any]]:
        if self.game is None:
            return None
        if self.game.network and self.game.network.p_id != -1 and self.game.server_players:
            return self.game.server_players.get(self.game.network.p_id)
        if self.game.player is not None and self.game.server_players:
            return self.game.server_players.get(str(self.game.network.p_id) if self.game.network else None)
        return None

    def _player_position(self) -> Optional[Tuple[float, float]]:
        if self.game and self.game.player is not None:
            return self.game.player.pos.x, self.game.player.pos.y
        if self.game and self.game.server_players:
            player = self.game.server_players.get(self.game.network.p_id if self.game.network else None)
            if player:
                return player.get("x", 0), player.get("y", 0)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        panel = pygame.Surface((WIDTH - 40, HEIGHT - 40), pygame.SRCALPHA)
        panel.fill((8, 8, 12, 180))
        surface.blit(panel, (20, 20))

        title = self.font.render("Developer Console", True, (220, 220, 220))
        surface.blit(title, (32, 32))

        output_y = 70
        max_lines = 20
        for entry in self.output[-max_lines:]:
            color = {
                "INFO": (90, 220, 120),
                "WARNING": (245, 190, 70),
                "ERROR": (255, 90, 90),
            }.get(entry["level"], (220, 220, 220))
            text = self.font.render(entry["text"], True, color)
            surface.blit(text, (32, output_y))
            output_y += 22

        prompt_y = HEIGHT - 70
        prompt_text = self.font.render(self.prompt + self.current_input, True, (255, 255, 255))
        surface.blit(prompt_text, (32, prompt_y))

        if self.autocomplete:
            hint = self.font.render(f"Tab: {self.autocomplete}", True, (140, 180, 255))
            surface.blit(hint, (32, prompt_y + 24))

        cursor_x = 32 + self.font.size(self.prompt + self.current_input[: self.cursor])[0]
        pygame.draw.line(surface, (255, 255, 255), (cursor_x, prompt_y + 2), (cursor_x, prompt_y + 18), 1)
