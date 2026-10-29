"""Модуль реализации кольцевого двусвязного списка, узла и плейлиста."""


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class LinkedListItem:
    """Узел кольцевого двусвязного списка."""

    def __init__(self, data):
        """Инициализация узла."""
        self.data = data
        self.track = data
        self._next_item = None
        self._previous_item = None

    def __eq__(self, other):
        """Сравнение узла с другим узлом или значением."""
        if isinstance(other, LinkedListItem):
            return self is other
        return other in (self.data, self.track)

    def __repr__(self):
        """Строковое представление узла."""
        return f"LinkedListItem({self.data})"

    @property
    def next_item(self):
        """Ссылка на следующий узел."""
        return self._next_item

    @next_item.setter
    def next_item(self, value):
        self._next_item = value
        if value is not None:
            # pylint: disable=protected-access
            if getattr(value, "_previous_item", None) != self:
                if hasattr(value, "_previous_item") and value._previous_item != self:
                    value._previous_item = self

    @property
    def previous_item(self):
        """Ссылка на предыдущий узел."""
        return self._previous_item

    @previous_item.setter
    def previous_item(self, value):
        self._previous_item = value
        if value is not None:
            # pylint: disable=protected-access
            if getattr(value, "_next_item", None) != self:
                if hasattr(value, "_next_item") and value._next_item != self:
                    value._next_item = self

    @property
    def next(self):
        """Псевдоним для совместимости с GUI."""
        return self._next_item

    @next.setter
    def next(self, value):
        self.next_item = value

    @property
    def prev(self):
        """Псевдоним для совместимости с GUI."""
        return self._previous_item

    @prev.setter
    def prev(self, value):
        self.previous_item = value


class LinkedList:
    """Кольцевой двусвязный список."""

    def __init__(self, start_node=None):
        """Инициализация списка."""
        self.head = start_node
        self._size = 0
        self._iter_curr = None
        self._iter_count = 0
        if start_node is not None:
            curr = start_node
            while True:
                self._size += 1
                curr = curr.next_item
                if curr == start_node or curr is None:
                    break

    def __len__(self):
        """Возвращает размер списка."""
        return self._size

    def __iter__(self):
        """Итератор по списку."""
        self._iter_curr = self.head
        self._iter_count = 0
        return self

    def __next__(self):
        """Возвращает следующий элемент при итерации."""
        if not self.head or self._iter_count >= self._size:
            raise StopIteration
        item = self._iter_curr
        self._iter_curr = self._iter_curr.next_item
        self._iter_count += 1
        return item

    def __getitem__(self, index):
        """Получение узла по индексу."""
        if not self.head or self._size == 0:
            raise IndexError("List index out of range")
        if not isinstance(index, int):
            raise TypeError("Indices must be integers")

        size = self._size
        if index < 0:
            index += size
        if not 0 <= index < size:
            raise IndexError("List index out of range")

        curr = self.head
        for _ in range(index):
            curr = curr.next_item
        return curr

    def __contains__(self, item):
        """Проверка наличия элемента."""
        if not self.head:
            return False
        curr = self.head
        for _ in range(self._size):
            if item in (curr, curr.data, curr.track):
                return True
            curr = curr.next_item
        return False

    @property
    def first_item(self):
        """Свойство для тестов, возвращающее head."""
        return self.head

    @first_item.setter
    def first_item(self, value):
        self.head = value

    @property
    def last(self):
        """Свойство, возвращающее последний узел."""
        if not self.head:
            return None
        return self.head.previous_item

    def append_right(self, item):
        """Добавление элемента в конец списка."""
        new_node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if not self.head:
            new_node.next_item = new_node
            new_node.previous_item = new_node
            self.head = new_node
        else:
            tail = self.head.previous_item
            tail.next_item = new_node
            new_node.previous_item = tail
            new_node.next_item = self.head
            self.head.previous_item = new_node
        self._size += 1

    def append(self, item):
        """Алиас для append_right."""
        self.append_right(item)

    def append_left(self, item):
        """Добавление элемента в начало списка."""
        self.append_right(item)
        self.head = self.head.previous_item
        self._size -= 1
        self._size += 1

    def insert(self, previous, item):
        """Вставка элемента после указанного узла."""
        if not self.head or not previous:
            self.append_right(item)
            return

        new_node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        next_node = previous.next_item

        previous.next_item = new_node
        new_node.previous_item = previous
        new_node.next_item = next_node
        next_node.previous_item = new_node
        self._size += 1

    def remove(self, item):
        """Удаление элемента."""
        if not self.head:
            raise ValueError(f"{item} не найден в списке")

        curr = self.head
        target_node = None
        for _ in range(self._size):
            if item in (curr, curr.data, curr.track):
                target_node = curr
                break
            curr = curr.next_item

        if target_node is None:
            raise ValueError(f"{item} не найден в списке")

        if self._size == 1:
            self.head = None
            self._size = 0
            return

        target_node.previous_item.next_item = target_node.next_item
        target_node.next_item.previous_item = target_node.previous_item

        if self.head == target_node:
            self.head = target_node.next_item

        self._size -= 1

    def move_node(self, node, direction):
        """Перемещение узла вверх или вниз."""
        if not node or self._size <= 1:
            return

        if direction == "up":
            target = node.previous_item
            if target == node:
                return

            is_moving_first = (node == self.head)

            node.previous_item.next_item = node.next_item
            node.next_item.previous_item = node.previous_item

            prev_target = target.previous_item
            prev_target.next_item = node
            node.previous_item = prev_target
            node.next_item = target
            target.previous_item = node

            if is_moving_first:
                self.head = node.next_item
            elif self.head == target:
                self.head = node

        elif direction == "down":
            target = node.next_item
            if target == node:
                return

            is_moving_last = (node == self.head.previous_item)

            node.previous_item.next_item = node.next_item
            node.next_item.previous_item = node.previous_item

            next_target = target.next_item
            target.next_item = node
            node.previous_item = target
            node.next_item = next_target
            next_target.previous_item = node

            if self.head == node:
                self.head = target
            elif is_moving_last:
                self.head = node

    def get_all(self):
        """Возвращает все данные в виде списка."""
        elements = []
        if not self.head:
            return elements
        curr = self.head
        for _ in range(self._size):
            elements.append(curr.data)
            curr = curr.next_item
        return elements


class Composition:
    """Класс музыкальной композиции."""

    def __init__(self, title, path):
        """Инициализация композиции."""
        self.title = title
        self.path = path

    def __str__(self):
        """Строковое представление композиции."""
        return self.title


class PlayList(LinkedList):
    """Класс управления плейлистом."""

    def __init__(self, name="По умолчанию"):
        """Инициализация плейлиста."""
        super().__init__()
        self.name = name
        self.list = self
        self._current_item = None

    @property
    def current_item(self):
        """Текущий элемент."""
        return self._current_item

    @current_item.setter
    def current_item(self, value):
        self._current_item = value

    @property
    def current(self):
        """Данные текущего элемента."""
        if self._current_item:
            return self._current_item.data
        return None

    def next_track(self):
        """Переход к следующему треку."""
        if not self.head:
            return None
        if self._current_item and self._current_item.next_item:
            self._current_item = self._current_item.next_item
        else:
            self._current_item = self.head
        return self._current_item.data

    def previous_track(self):
        """Переход к предыдущему треку."""
        if not self.head:
            return None
        if self._current_item and self._current_item.previous_item:
            self._current_item = self._current_item.previous_item
        else:
            self._current_item = self.head.previous_item
        return self._current_item.data

    def add_track(self, title, path):
        """Добавление трека."""
        comp = Composition(title, path)
        self.append(comp)
        if not self._current_item:
            self._current_item = self.head

    def remove(self, item):
        """Удаление трека с учетом текущего."""
        target_node = item if isinstance(item, LinkedListItem) else None
        if not target_node and self.head:
            curr = self.head
            for _ in range(self._size):
                if item in (curr, curr.data, curr.track):
                    target_node = curr
                    break
                curr = curr.next_item

        if target_node:
            if self._current_item == target_node:
                if self._size > 1:
                    self._current_item = target_node.next_item
                else:
                    self._current_item = None
            super().remove(target_node)

    def move_current(self, direction):
        """Перемещение текущего трека."""
        if self._current_item:
            self.move_node(self._current_item, direction)
