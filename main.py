import flet as ft
import time
import threading

class PomodoroTimer:
    def __init__(self):
        # タイマーの初期設定
        self.WORK_TIME = 25 * 60  # 25分
        self.BREAK_TIME = 5 * 60  # 5分
        self.time_left = self.WORK_TIME
        self.is_work_mode = True
        self.is_running = False
        self.timer_thread = None

class PomodoroApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.timer = PomodoroTimer()

    def build(self):
        # UI要素の初期化
        self.mode_text = ft.Text(
            "作業時間",
            size=30,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD
        )
        
        self.time_display = ft.Text(
            "25:00",
            size=60,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.BOLD
        )
        
        self.progress_bar = ft.ProgressBar(
            width=400,
            height=20,
            color=ft.colors.BLUE,
            bgcolor=ft.colors.BLUE_100,
            value=1.0
        )
        
        self.start_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            icon_color=ft.colors.GREEN,
            icon_size=40,
            tooltip="開始",
            on_click=self.toggle_timer
        )
        
        self.reset_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            icon_color=ft.colors.RED,
            icon_size=40,
            tooltip="リセット",
            on_click=self.reset_timer
        )

        # レイアウトの構築
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.mode_text,
                    self.time_display,
                    self.progress_bar,
                    ft.Row(
                        controls=[
                            self.start_button,
                            self.reset_button
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20
        )

    def format_time(self, seconds):
        """秒を MM:SS 形式に変換"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_display(self):
        """表示の更新"""
        self.time_display.value = self.format_time(self.timer.time_left)
        total_time = self.timer.WORK_TIME if self.timer.is_work_mode else self.timer.BREAK_TIME
        self.progress_bar.value = self.timer.time_left / total_time
        self.update()

    def timer_tick(self):
        """タイマーのメインロジック"""
        while self.timer.is_running and self.timer.time_left > 0:
            time.sleep(1)
            self.timer.time_left -= 1
            self.update_display()

        if self.timer.time_left <= 0 and self.timer.is_running:
            self.play_notification()
            self.switch_mode()

    def toggle_timer(self, e):
        """タイマーの開始/一時停止"""
        if not self.timer.is_running:
            self.timer.is_running = True
            self.start_button.icon = ft.icons.PAUSE
            self.start_button.icon_color = ft.colors.ORANGE
            self.timer_thread = threading.Thread(target=self.timer_tick, daemon=True)
            self.timer_thread.start()
        else:
            self.timer.is_running = False
            self.start_button.icon = ft.icons.PLAY_ARROW
            self.start_button.icon_color = ft.colors.GREEN
        self.update()

    def reset_timer(self, e):
        """タイマーのリセット"""
        self.timer.is_running = False
        self.timer.is_work_mode = True
        self.timer.time_left = self.timer.WORK_TIME
        self.mode_text.value = "作業時間"
        self.start_button.icon = ft.icons.PLAY_ARROW
        self.start_button.icon_color = ft.colors.GREEN
        self.update_display()

    def switch_mode(self):
        """作業/休憩モードの切り替え"""
        self.timer.is_work_mode = not self.timer.is_work_mode
        self.timer.time_left = self.timer.WORK_TIME if self.timer.is_work_mode else self.timer.BREAK_TIME
        self.mode_text.value = "作業時間" if self.timer.is_work_mode else "休憩時間"
        self.progress_bar.color = ft.colors.BLUE if self.timer.is_work_mode else ft.colors.GREEN
        self.update_display()

    def play_notification(self):
        """通知ダイアログの表示"""
        mode = "作業" if self.timer.is_work_mode else "休憩"
        dialog = ft.AlertDialog(
            title=ft.Text(f"{mode}時間が終了しました！"),
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

def main(page: ft.Page):
    page.title = "ポモドーロタイマー"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # アプリケーションの追加
    pomodoro_app = PomodoroApp()
    page.add(pomodoro_app)

if __name__ == "__main__":
    ft.app(target=main)