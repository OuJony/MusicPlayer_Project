"""
Графический интерфейс музыкального плеера на базе Tkinter и Pygame.
Cначала нужно запустить player_GUI.py
Инструкция:
Нужно ввести в терминал (VS Code):
1)python -m venv venv
2)source venv/Scripts/activate
3) pip install -r requirements.txt
4)python player_gui.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame

from linked_list import Composition, PlayList


class MusicPlayerApp:
    """Класс графического приложения музыкального плеера."""

    def __init__(self, master_root: tk.Tk) -> None:
        self.root = master_root
        self.root.title("Музыкальный плеер (Кольцевой двусвязный список)")
        self.root.geometry("600x450")
        self.root.config(bg="#f0f0f0")

        # Инициализация микшера Pygame
        pygame.mixer.init()

        # Инициализация плейлиста
        self.playlist = PlayList()

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self) -> None:
        """Создание элементов управления и списков на форме."""
        self.track_listbox = tk.Listbox(
            self.root, font=("Arial", 11), selectbackground="#b0c4de", width=50, height=15
        )
        self.track_listbox.pack(pady=15)

        file_frame = tk.Frame(self.root, bg="#f0f0f0")
        file_frame.pack(pady=5)

        btn_add = tk.Button(file_frame, text="Добавить трек", width=15, command=self.add_track)
        btn_add.grid(row=0, column=0, padx=5)

        btn_remove = tk.Button(file_frame, text="Удалить трек", width=15, command=self.remove_track)
        btn_remove.grid(row=0, column=1, padx=5)

        btn_up = tk.Button(file_frame, text="Выше ↑", width=10, command=lambda: self.move_track("up"))
        btn_up.grid(row=0, column=2, padx=5)

        btn_down = tk.Button(file_frame, text="Ниже ↓", width=10, command=lambda: self.move_track("down"))
        btn_down.grid(row=0, column=3, padx=5)

        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(pady=15)

        btn_prev = tk.Button(control_frame, text="⏮ Предыдущий", width=15, command=self.prev_track)
        btn_prev.grid(row=0, column=0, padx=5)

        btn_play = tk.Button(control_frame, text="▶ Воспроизвести", width=15, command=self.play_track)
        btn_play.grid(row=0, column=1, padx=5)

        btn_next = tk.Button(control_frame, text="⏭ Следующий", width=15, command=self.next_track)
        btn_next.grid(row=0, column=2, padx=5)

        btn_stop = tk.Button(control_frame, text="⏹ Стоп", width=15, command=self.stop_track)
        btn_stop.grid(row=0, column=3, padx=5)

        self.status_label = tk.Label(
            self.root, text="Сейчас играет: нет", font=("Arial", 10, "italic"), bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)

    def refresh_listbox(self) -> None:
        """Обновление отображения списка в интерфейсе."""
        self.track_listbox.delete(0, tk.END)
        if len(self.playlist) == 0:
            return

        current = self.playlist.first_item
        start = current
        while True:
            display_text = current.track.title
            if self.playlist.current_item == current:
                display_text = "▶ " + display_text
            self.track_listbox.insert(tk.END, display_text)
            current = current.next_item
            if current == start:
                break

    def add_track(self) -> None:
        """Добавление музыкального файла в плейлист."""
        file_path = filedialog.askopenfilename(
            title="Выберите аудио файл",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            track = Composition(title=filename, file_path=file_path)
            self.playlist.append(track)
            if not self.playlist.current_item:
                self.playlist.current_item = self.playlist.first_item
            self.refresh_listbox()

    def remove_track(self) -> None:
        """Удаление выбранного трека из плейлиста."""
        try:
            selected_index = self.track_listbox.curselection()[0]
            track_to_remove = self.playlist[selected_index]
            self.playlist.remove(track_to_remove)
            self.refresh_listbox()
            self.status_label.config(text="Трек удален")
        except IndexError:
            messagebox.showwarning("Внимание", "Выберите трек для удаления!")

    def move_track(self, direction: str) -> None:
        """Перемещение трека вверх или вниз."""
        try:
            selected_index = self.track_listbox.curselection()[0]
            track = self.playlist[selected_index]
            if direction == "up":
                self.playlist.move_up(track)
            else:
                self.playlist.move_down(track)
            self.refresh_listbox()
        except IndexError:
            messagebox.showwarning("Внимание", "Выберите трек для перемещения!")

    def play_track(self) -> None:
        """Запуск выбранного или текущего трека."""
        try:
            selected_index = self.track_listbox.curselection()[0]
            track = self.playlist[selected_index]
            self.playlist.play_all(track)
        except IndexError:
            if not self.playlist.current:
                messagebox.showwarning("Внимание", "Плейлист пуст или трек не выбран!")
                return

        current_track = self.playlist.current
        if current_track:
            try:
                pygame.mixer.music.load(current_track.file_path)
                pygame.mixer.music.play()
                self.status_label.config(text=f"Сейчас играет: {current_track.title}")
                self.refresh_listbox()
            except pygame.error as e:  # pylint: disable=no-member
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл:\n{e}")

    def next_track(self) -> None:
        """Переключение на следующий трек с автоматическим кольцевым циклом."""
        if len(self.playlist) == 0:
            return
        self.playlist.next_track()
        current_track = self.playlist.current
        if current_track:
            try:
                pygame.mixer.music.load(current_track.file_path)
                pygame.mixer.music.play()
                self.status_label.config(text=f"Сейчас играет: {current_track.title}")
                self.refresh_listbox()
            except pygame.error as e:  # pylint: disable=no-member
                messagebox.showerror("Ошибка", f"{e}")

    def prev_track(self) -> None:
        """Переключение на предыдущий трек."""
        if len(self.playlist) == 0:
            return
        self.playlist.previous_track()
        current_track = self.playlist.current
        if current_track:
            try:
                pygame.mixer.music.load(current_track.file_path)
                pygame.mixer.music.play()
                self.status_label.config(text=f"Сейчас играет: {current_track.title}")
                self.refresh_listbox()
            except pygame.error as e:  # pylint: disable=no-member
                messagebox.showerror("Ошибка", f"{e}")

    def stop_track(self) -> None:
        """Остановка воспроизведения текущего трека."""
        pygame.mixer.music.stop()
        self.status_label.config(text="Воспроизведение остановлено")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
