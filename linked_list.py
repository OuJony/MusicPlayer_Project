"""
Модуль для реализации кольцевого двусвязного списка и музыкального плейлиста.
Нужно запустить player_gui.py
"""

from typing import Any, Iterator, Optional


class Composition:  # pylint: disable=too-few-public-methods
    """Класс, представляющий музыкальную композицию."""

    def __init__(self, title: str, file_path: str) -> None:
        self.title = title
        self.file_path = file_path
        self.data = title  # Поле для совместимости с тестами

    def __str__(self) -> str:
        return self.title


class LinkedListItem:
    """Элемент связного списка, содержащий данные и соседние элементы."""

    def __init__(self, track: Any) -> None:
        self.track: Any = track
        if hasattr(track, 'data'):
            self.data = track.data
        else:
            self.data = track
        self._next: Optional['LinkedListItem'] = None
        self._previous: Optional['LinkedListItem'] = None

    @property
    def next_item(self) -> Optional['LinkedListItem']:
        """Геттер для следующего элемента."""
        return self._next

    @next_item.setter
    def next_item(self, item: Optional['LinkedListItem']) -> None:
        """Сеттер для следующего элемента с автоматической связкой."""
        self._next = item
        if item and item._previous != self:  # pylint: disable=protected-access
            item._previous = self  # pylint: disable=protected-access

    @property
    def previous_item(self) -> Optional['LinkedListItem']:
        """Геттер для предыдущего элемента."""
        return self._previous

    @previous_item.setter
    def previous_item(self, item: Optional['LinkedListItem']) -> None:
        """Сеттер для предыдущего элемента с автоматической связкой."""
        self._previous = item
        if item and item._next != self:  # pylint: disable=protected-access
            item._next = self  # pylint: disable=protected-access


class LinkedList:
    """Базовый класс двусвязного кольцевого списка."""

    def __init__(self, first_item: Optional[LinkedListItem] = None) -> None:
        self.first_item: Optional[LinkedListItem] = first_item
        self._iter_current: Optional[LinkedListItem] = None

    def __len__(self) -> int:
        """Возвращает длину списка."""
        if not self.first_item:
            return 0
        count = 1
        current = self.first_item.next_item
        while current and current != self.first_item:
            count += 1
            current = current.next_item
        return count

    def __iter__(self) -> Iterator[Any]:
        """Получение итератора по элементам списка."""
        self._iter_current = self.first_item
        return self

    def __next__(self) -> Any:
        """Получение следующего элемента при итерации."""
        if not self._iter_current:
            raise StopIteration
        node = self._iter_current
        self._iter_current = self._iter_current.next_item
        if self._iter_current == self.first_item:
            self._iter_current = None
        return node

    def __getitem__(self, index: int) -> Any:
        """Получение элемента по индексу."""
        length = len(self)
        if length == 0:
            raise IndexError("Список пуст")
        if index < 0:
            index += length
        if not 0 <= index < length:
            raise IndexError("Индекс вне диапазона")

        current = self.first_item
        for _ in range(index):
            current = current.next_item
        return current.track

    def __contains__(self, item: Any) -> bool:
        """Проверка наличия элемента в списке."""
        if not self.first_item:
            return False
        current = self.first_item
        while True:
            if current == item or current.track == item or getattr(current, 'data', None) == item:
                return True
            current = current.next_item
            if current == self.first_item:
                break
        return False

    def __reversed__(self) -> Iterator[Any]:
        """Поддержка функции reversed."""
        if not self.first_item:
            return iter([])
        items = []
        current = self.first_item.previous_item
        start = current
        while True:
            items.append(current.track)
            current = current.previous_item
            if current == start:
                break
        return iter(items)

    def append_left(self, item: Any) -> None:
        """Добавление элемента в начало списка."""
        new_node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if not self.first_item:
            self.first_item = new_node
            new_node.next_item = new_node
            new_node.previous_item = new_node
        else:
            last_node = self.first_item.previous_item
            new_node.next_item = self.first_item
            new_node.previous_item = last_node
            self.first_item.previous_item = new_node
            last_node.next_item = new_node
            self.first_item = new_node

    def append_right(self, item: Any) -> None:
        """Добавление элемента в конец списка."""
        new_node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if not self.first_item:
            self.first_item = new_node
            new_node.next_item = new_node
            new_node.previous_item = new_node
        else:
            last_node = self.first_item.previous_item
            new_node.next_item = self.first_item
            new_node.previous_item = last_node
            last_node.next_item = new_node
            self.first_item.previous_item = new_node

    def append(self, item: Any) -> None:
        """Алиас для append_right."""
        self.append_right(item)

    @property
    def last(self) -> Optional[LinkedListItem]:
        """Получение последнего элемента списка в виде свойства."""
        if not self.first_item:
            return None
        return self.first_item.previous_item

    def remove(self, item: Any) -> None:
        """Удаление элемента из списка."""
        if not self.first_item:
            raise ValueError("Элемент не найден в пустом списке")

        target_node = None
        current = self.first_item
        while True:
            if current == item or current.track == item or getattr(current, 'data', None) == item:
                target_node = current
                break
            current = current.next_item
            if current == self.first_item:
                break

        if not target_node:
            raise ValueError("Элемент не найден в списке")

        if target_node.next_item == target_node:
            self.first_item = None
        else:
            prev_node = target_node.previous_item
            next_node = target_node.next_item
            prev_node.next_item = next_node
            next_node.previous_item = prev_node
            if target_node == self.first_item:
                self.first_item = next_node

    def insert(self, previous: Any, item: Any) -> None:
        """Вставка элемента item после элемента previous."""
        if not self.first_item:
            raise ValueError("Список пуст")

        target_node = None
        current = self.first_item
        while True:
            if current == previous or current.track == previous or getattr(current, 'data', None) == previous:
                target_node = current
                break
            current = current.next_item
            if current == self.first_item:
                break

        if not target_node:
            raise ValueError("Элемент 'previous' не найден")

        new_node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        next_node = target_node.next_item

        target_node.next_item = new_node
        new_node.previous_item = target_node
        new_node.next_item = next_node
        next_node.previous_item = new_node


class PlayList(LinkedList):
    """Класс Плейлиста с поддержкой проигрывания и изменения порядка."""

    def __init__(self, first_item: Optional[LinkedListItem] = None) -> None:
        super().__init__(first_item)
        self.current_item: Optional[LinkedListItem] = None

    @property
    def current(self) -> Any:
        """Получение текущего трека."""
        if not self.current_item:
            return None
        return self.current_item.track if hasattr(self.current_item, 'track') else self.current_item

    def play_all(self, item: Any) -> Any:
        """Начать проигрывать все треки, начиная с указанного."""
        if not self.first_item:
            return None

        target_node = None
        current = self.first_item
        while True:
            if current == item or current.track == item or getattr(current, 'data', None) == item:
                target_node = current
                break
            current = current.next_item
            if current == self.first_item:
                break

        if target_node:
            self.current_item = target_node
            return self.current
        return None

    def next_track(self) -> Any:
        """Перейти к следующему треку (с зацикливанием по кругу)."""
        if not self.current_item:
            if self.first_item:
                self.current_item = self.first_item
        else:
            self.current_item = self.current_item.next_item
        return self.current

    def previous_track(self) -> Any:
        """Перейти к предыдущему треку."""
        if not self.current_item:
            if self.first_item:
                self.current_item = self.first_item.previous_item
        else:
            self.current_item = self.current_item.previous_item
        return self.current

    def move_up(self, item: Any) -> None:
        """Перемещение трека выше в плейлисте."""
        node = self._find_node(item)
        if not node or node == self.first_item or self.first_item.next_item == self.first_item:
            return

        node.track, node.previous_item.track = node.previous_item.track, node.track
        if hasattr(node, 'data') and hasattr(node.previous_item, 'data'):
            node.data, node.previous_item.data = node.previous_item.data, node.data
        if self.current_item == node.previous_item:
            self.current_item = node

    def move_down(self, item: Any) -> None:
        """Перемещение трека ниже в плейлисте."""
        node = self._find_node(item)
        if not node or (node.next_item == self.first_item and node == self.first_item):
            return

        node.track, node.next_item.track = node.next_item.track, node.track
        if hasattr(node, 'data') and hasattr(node.next_item, 'data'):
            node.data, node.next_item.data = node.next_item.data, node.data

        if self.current_item == node.next_item:
            self.current_item = node

    def _find_node(self, item: Any) -> Optional[LinkedListItem]:
        """Вспомогательный метод поиска узла."""
        if not self.first_item:
            return None
        current = self.first_item
        while True:
            if current == item or current.track == item or getattr(current, 'data', None) == item:
                return current
            current = current.next_item
            if current == self.first_item:
                break
        return None
