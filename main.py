import flet as ft
import time
from datetime import datetime
import threading

class PomodoroTimer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "ポモドーロタイマー"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # 状態管理
        self.work_time = 25 * 60  # 25分
        self.break_time = 5 * 60  # 5分
        self.time_left = self.work_time
        self.is_running = False
        self.is_work_mode = True
        self.timer_thread = None

        # UIコンポーネント
        self.mode_text = ft.Text(
            "作業時間",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_600
        )

        self.time_display = ft.Text(
            self._format_time(self.time_left),
            size=60,
            weight=ft.FontWeight.BOLD
        )

        self.progress_bar = ft.ProgressBar(
            width=400,
            color=ft.colors.BLUE_400,
            bgcolor=ft.colors.BLUE_100
        )

        # ボタン
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

        # レイアウト構築
        self._build_layout()
        self._update_progress_bar()

    def _build_layout(self):
        """UIレイアウトの構築"""
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.mode_text,
                        self.time_display,
                        self.progress_bar,
                        ft.Row(
                            controls=[self.start_button, self.reset_button],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.colors.BLUE_GREY_100,
                )
            )
        )

    def _format_time(self, seconds: int) -> str:
        """秒を MM:SS 形式に変換"""
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _update_progress_bar(self):
        """プログレスバーの更新"""
        total_time = self.work_time if self.is_work_mode else self.break_time
        self.progress_bar.value = self.time_left / total_time
        self.page.update()

    def toggle_timer(self, e):
        """タイマーの開始/停止の切り替え"""
        if not self.is_running:
            self.is_running = True
            self.start_button.icon = ft.icons.PAUSE
            self.start_button.icon_color = ft.colors.ORANGE
            self.start_button.tooltip = "一時停止"
            
            # タイマースレッドの開始
            self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self.timer_thread.start()
        else:
            self.is_running = False
            self.start_button.icon = ft.icons.PLAY_ARROW
            self.start_button.icon_color = ft.colors.GREEN
            self.start_button.tooltip = "開始"
        self.page.update()

    def reset_timer(self, e):
        """タイマーのリセット"""
        self.is_running = False
        self.time_left = self.work_time
        self.is_work_mode = True
        self.mode_text.value = "作業時間"
        self.mode_text.color = ft.colors.BLUE_600
        self.time_display.value = self._format_time(self.time_left)
        self.start_button.icon = ft.icons.PLAY_ARROW
        self.start_button.icon_color = ft.colors.GREEN
        self.start_button.tooltip = "開始"
        self._update_progress_bar()
        self.page.update()

    def _run_timer(self):
        """タイマーのメインロジック"""
        while self.is_running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            self.time_display.value = self._format_time(self.time_left)
            self._update_progress_bar()
            
            if self.time_left == 0:
                self._timer_completed()

    def _timer_completed(self):
        """タイマー完了時の処理"""
        self.is_work_mode = not self.is_work_mode
        
        if self.is_work_mode:
            self.time_left = self.work_time
            self.mode_text.value = "作業時間"
            self.mode_text.color = ft.colors.BLUE_600
            self._show_notification("休憩終了", "作業を開始してください")
        else:
            self.time_left = self.break_time
            self.mode_text.value = "休憩時間"
            self.mode_text.color = ft.colors.GREEN_600
            self._show_notification("作業終了", "休憩を取りましょう")
        
        self.is_running = False
        self.start_button.icon = ft.icons.PLAY_ARROW
        self.start_button.icon_color = ft.colors.GREEN
        self._update_progress_bar()
        self.page.update()

    def _show_notification(self, title: str, message: str):
        """通知ダイアログの表示"""
        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dlg)
            ],
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

def main(page: ft.Page):
    page.bgcolor = ft.colors.BLUE_50
    app = PomodoroTimer(page)

if __name__ == "__main__":
    ft.app(target=main)