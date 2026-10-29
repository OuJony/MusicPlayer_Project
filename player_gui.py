# pylint: disable=import-error
"""Графический интерфейс музыкального плеера на основе Tkinter и Pygame.
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
from tkinter import filedialog, messagebox, simpledialog
import pygame
from linked_list import PlayList


# pylint: disable=too-many-instance-attributes
class MusicPlayerApp:
    """Класс графического приложения музыкального плеера."""

    def __init__(self, master_root: tk.Tk) -> None:
        """Инициализация главного окна и компонентов плеера."""
        self.root = master_root
        self.root.title("Музыкальный плеер")
        self.root.geometry("620x520")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error as exc:
            messagebox.showerror("Ошибка Pygame", f"Не удалось инициализировать звук: {exc}")

        self._was_playing = False
        self._is_paused = False

        self.playlists = {"По умолчанию": PlayList("По умолчанию")}
        self.current_playlist_name = "По умолчанию"

        self.create_widgets()
        self.check_music_events()

    @property
    def current_playlist(self) -> PlayList:
        """Свойство для получения активного плейлиста."""
        return self.playlists[self.current_playlist_name]

    def create_widgets(self) -> None:
        """Создание и размещение элементов GUI."""
        playlist_frame = tk.Frame(self.root)
        playlist_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(playlist_frame, text="Плейлист:").pack(side=tk.LEFT, padx=5)
        self.playlist_var = tk.StringVar(value=self.current_playlist_name)
        self.playlist_menu = tk.OptionMenu(
            playlist_frame,
            self.playlist_var,
            *self.playlists.keys(),
            command=self.on_playlist_change
        )
        self.playlist_menu.pack(side=tk.LEFT, padx=5)

        tk.Button(playlist_frame, text="+ Плейлист", command=self.add_playlist).pack(side=tk.LEFT, padx=2)
        tk.Button(playlist_frame, text="- Плейлист", command=self.delete_playlist).pack(side=tk.LEFT, padx=2)

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.track_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.track_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.track_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        scrollbar = tk.Scrollbar(list_frame, command=self.track_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.track_listbox.config(yscrollcommand=scrollbar.set)

        action_frame = tk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(action_frame, text="Добавить трек", command=self.add_track).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Удалить трек", command=self.remove_track).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="▲ Вверх", command=self.move_up).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="▼ Вниз", command=self.move_down).pack(side=tk.LEFT, padx=5)

        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(control_frame, text="◄◄ Пред.", command=self.prev_track).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="▶ Старт", command=self.play_track).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="❚❚ Пауза", command=self.pause_track).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="■ Стоп", command=self.stop_track).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="След. ►►", command=self.next_track).pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.root, text="Готов к работе", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def check_music_events(self) -> None:
        """Проверяет завершение текущего трека (автопереключение)."""
        if not pygame.mixer.music.get_busy() and self._was_playing and not self._is_paused:
            self._was_playing = False
            self.next_track()

        self.root.after(500, self.check_music_events)

    def update_listbox(self) -> None:
        """Обновляет отображение списка треков в Listbox."""
        self.track_listbox.delete(0, tk.END)
        tracks = self.current_playlist.list.get_all()
        current_node = self.current_playlist.list.current_item

        for i, comp in enumerate(tracks):
            is_current = False
            curr = self.current_playlist.list.head
            if curr:
                for _ in range(self.current_playlist.list._size):  # pylint: disable=protected-access
                    if curr.data == comp and curr == current_node:
                        is_current = True
                        break
                    curr = curr.next_item

            prefix = "▶ " if is_current else "   "
            self.track_listbox.insert(tk.END, f"{prefix}{i + 1}. {comp.title}")

    def on_listbox_select(self, _event) -> None:
        """Синхронизирует выбор в Listbox с текущим узлом списка."""
        selection = self.track_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        try:
            node = self.current_playlist.list[index]
            self.current_playlist.list.current_item = node
            self.update_listbox()
        except (IndexError, TypeError):
            pass

    def on_playlist_change(self, selected_name: str) -> None:
        """Переключает текущий активный плейлист."""
        self.current_playlist_name = selected_name
        self.update_listbox()

    def add_playlist(self) -> None:
        """Создает новый плейлист с заданным именем."""
        name = simpledialog.askstring("Новый плейлист", "Введите название плейлиста:")
        if name:
            name = name.strip()
            if name and name not in self.playlists:
                self.playlists[name] = PlayList(name)
                self.update_playlist_menu()
                self.playlist_var.set(name)
                self.on_playlist_change(name)

    def delete_playlist(self) -> None:
        """Удаляет текущий плейлист."""
        if len(self.playlists) <= 1:
            messagebox.showwarning("Ошибка", "Нельзя удалить единственный плейлист!")
            return
        del self.playlists[self.current_playlist_name]
        self.current_playlist_name = list(self.playlists.keys())[0]
        self.update_playlist_menu()
        self.playlist_var.set(self.current_playlist_name)
        self.on_playlist_change(self.current_playlist_name)

    def update_playlist_menu(self) -> None:
        """Обновляет выпадающее меню выбора плейлистов."""
        menu = self.playlist_menu["menu"]
        menu.delete(0, "end")
        for name in self.playlists:
            menu.add_command(
                label=name,
                command=lambda value=name: [
                    self.playlist_var.set(value),
                    self.on_playlist_change(value)
                ]
            )

    def add_track(self) -> None:
        """Добавляет аудиофайл в текущий плейлист."""
        filepaths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        for path in filepaths:
            title = os.path.basename(path)
            self.current_playlist.add_track(title, path)
        self.update_listbox()

    def remove_track(self) -> None:
        """Удаляет выделенный/текущий трек из плейлиста."""
        clist = self.current_playlist.list
        if len(clist) == 0:
            return

        if clist.current_item:
            clist.remove(clist.current_item)
            pygame.mixer.music.stop()
            self._was_playing = False
            self._is_paused = False
            self.status_label.config(text="Трек удален")
        self.update_listbox()

    def move_up(self) -> None:
        """Перемещает текущий трек вверх."""
        if self.current_playlist.list.current_item:
            self.current_playlist.move_current("up")
            self.update_listbox()

    def move_down(self) -> None:
        """Перемещает текущий трек вниз."""
        if self.current_playlist.list.current_item:
            self.current_playlist.move_current("down")
            self.update_listbox()

    def play_track(self) -> None:
        """Запускает воспроизведение или продолжает с прерванного места."""
        clist = self.current_playlist.list
        if not clist.current_item:
            if clist.head:
                clist.current_item = clist.head
            else:
                self.status_label.config(text="Плейлист пуст")
                return

        comp = clist.current_item.data
        if comp and os.path.exists(comp.path):
            try:
                if self._is_paused:
                    pygame.mixer.music.unpause()
                    self._is_paused = False
                    self._was_playing = True
                    self.status_label.config(text=f"Играет: {comp.title}")
                    self.update_listbox()
                    return

                pygame.mixer.music.load(comp.path)
                pygame.mixer.music.play()
                self._is_paused = False
                self._was_playing = True
                self.status_label.config(text=f"Играет: {comp.title}")
                self.update_listbox()
            except pygame.error as exc:
                self.status_label.config(text=f"Ошибка воспроизведения: {exc}")
        else:
            path_str = comp.path if comp else "неизвестно"
            self.status_label.config(text=f"Файл не найден: {path_str}")

    def pause_track(self) -> None:
        """Ставит воспроизведение на паузу или снимает с нее."""
        if pygame.mixer.music.get_busy() and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self.status_label.config(text="Пауза")
        elif self._is_paused:
            self.play_track()
        else:
            self.play_track()

    def stop_track(self) -> None:
        """Останавливает воспроизведение и сбрасывает позицию."""
        pygame.mixer.music.stop()
        self._was_playing = False
        self._is_paused = False
        self.status_label.config(text="Остановлено")

    def next_track(self) -> None:
        """Переключает на следующий трек и запускает его."""
        clist = self.current_playlist.list
        if len(clist) > 0:
            clist.next_track()
            self.play_track()

    def prev_track(self) -> None:
        """Переключает на предыдущий трек и запускает его."""
        clist = self.current_playlist.list
        if len(clist) > 0:
            clist.previous_track()
            self.play_track()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
