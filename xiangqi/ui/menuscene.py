import pygame
from .scenes import Scene
from pathlib import Path
from .playscene import PlayScene
from .asset_manager import AssetManager
from .theme import Theme

class MenuScene(Scene):
    from .playscene import PlayScene
    def on_enter(self, **kwards):
        self.selected_mode = 0 # 0: 人机； 1: 换边； 2: 切换主题
        self.modes = ["HUMAN_VS_AI", "CHANGE_SIDE", "CHESS_CHALLENGE"]
        base_path = Path(__file__).parent.parent / 'assets' / 'img'
        self.init_bg = pygame.image.load(str(base_path / 'init_bg.png'))
        self.btn_bg = pygame.image.load(str(base_path / 'btn_bg.png'))

        self.swith_theme = AssetManager(self.game.theme)

        #我的字体文件目录
        font_path = base_path.parent /"fonts" / "NotoSerifSC-Regular.otf"
        self.font = pygame.font.Font(str(font_path), 20)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.selected_mode = 0
            elif event.key == pygame.K_2:
                self.selected_mode = 1
            elif event.key == pygame.K_3:
                self.selected_mode = 2
            elif event.key == pygame.K_RETURN:
                self.game.change_scene(PlayScene(self.game), mode=self.modes[self.selected_mode])
            elif event.key == pygame.K_m:
                pygame.mixer.music.pause() if pygame.mixer.music.get_busy() else pygame.mixer.music.unpause()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            print(f"Clicked on x={x}, y={y}")
            screen_w, screen_h = self.game.screen.get_size()
            init_bg_x = (screen_w - self.init_bg.get_width()) // 2
            init_bg_y = (screen_h - self.init_bg.get_height()) // 2
            menu_items = ["人机对弈", "换边对战", "切换主题"]
            start_y = init_bg_y + 180
            for i, _ in enumerate(menu_items):
                btn_x = init_bg_x + 50
                btn_rect = pygame.Rect(btn_x, start_y, self.btn_bg.get_width(), self.btn_bg.get_height())
                if btn_rect.collidepoint(x, y):
                    if i == 0:
                        self.game.change_scene(PlayScene(self.game), mode=self.modes[self.selected_mode])
                    elif i == 1:
                        self.game.change_scene(PlayScene(self.game), mode=self.modes[self.selected_mode])
                    elif i == 2:
                        self.switch_theme()
                start_y += 80


    def draw(self, screen: pygame.Surface):
        bg = self.game.assets.bg
        screen_w, screen_h = screen.get_size()
        bg_w, bg_h = bg.get_size()

        scale_x, scale_y= screen_w / bg_w, screen_h / bg_h
        scale = max(scale_x, scale_y)

        new_w = int(bg_w * scale)
        new_h = int(bg_h * scale)
        bg_scaled = pygame.transform.smoothscale(bg, (new_w, new_h))
        bg_x, bg_y= (screen_w - new_w) // 2, (screen_h - new_h) // 2
        screen.blit(bg_scaled, (bg_x, bg_y))

        init_bg_x = (screen_w - self.init_bg.get_width()) // 2
        init_bg_y = (screen_h - self.init_bg.get_height()) // 2
        screen.blit(self.init_bg, (init_bg_x, init_bg_y))

        menu_items = ["人机对弈", "换边对战", "切换主题"]
        start_y = init_bg_y + 180
        for mode, text in enumerate(menu_items):
            color = (255, 200, 0) if self.selected_mode == mode else (200, 200, 0)
            text_surf = self.font.render(text, True, color)
            btn_x = init_bg_x + 50
            screen.blit(self.btn_bg, (btn_x, start_y))
            text_rect = text_surf.get_rect(center=(btn_x + self.btn_bg.get_width() // 2, start_y + self.btn_bg.get_height() // 2))
            screen.blit(text_surf, text_rect)
            start_y += 80

        hint = self.font.render("按回车键开始游戏", True, (255, 255, 255))
        hint_rect = hint.get_rect(center=( screen_w // 2, start_y + 50))
        screen.blit(hint, hint_rect)

    def switch_theme(self):
        current_theme_name = self.game.assets.theme.name
        if current_theme_name == "风格一":
            new_theme = Theme.style_2()
        elif current_theme_name == "风格二":
            new_theme = Theme.style_3()
        else:
            new_theme = Theme.style_1()
        self.game.set_theme(new_theme)
