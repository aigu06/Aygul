import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = 'books.json'


class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Book Tracker')
        self.root.geometry('820x520')
        self.books = []

        # Форма добавления книги
        form = ttk.LabelFrame(root, text='Добавить книгу')
        form.pack(fill='x', padx=10, pady=10)

        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.pages_var = tk.StringVar()
        self.genre_filter_var = tk.StringVar()
        self.pages_filter_var = tk.StringVar(value='200')

        self._row(form, 0, 'Название книги', self.title_var)
        self._row(form, 1, 'Автор', self.author_var)
        self._row(form, 2, 'Жанр', self.genre_var)
        self._row(form, 3, 'Количество страниц', self.pages_var)

        ttk.Button(form, text='Добавить книгу', command=self.add_book).grid(
            row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=8
        )

        # Фильтры
        filters = ttk.LabelFrame(root, text='Фильтрация')
        filters.pack(fill='x', padx=10, pady=5)

        ttk.Label(filters, text='Жанр').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(filters, textvariable=self.genre_filter_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(filters, text='Страниц больше').grid(row=0, column=2, padx=5, pady=5, sticky='w')
        ttk.Entry(filters, textvariable=self.pages_filter_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(filters, text='Применить фильтр', command=self.refresh_table).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(filters, text='Сбросить фильтр', command=self.reset_filters).grid(row=0, column=5, padx=5, pady=5)

        # Таблица
        table_frame = ttk.Frame(root)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('title', 'author', 'genre', 'pages')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col, text, width in [
            ('title', 'Название', 220),
            ('author', 'Автор', 180),
            ('genre', 'Жанр', 150),
            ('pages', 'Страницы', 90),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor='w')
        self.tree.pack(side='left', fill='both', expand=True)
        ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview).pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=lambda *args: None)

        # Низ формы: кнопки сохранения/загрузки
        bottom = ttk.Frame(root)
        bottom.pack(fill='x', padx=10, pady=5)
        ttk.Button(bottom, text='Загрузить JSON', command=self.load_json).pack(side='left', padx=5)
        ttk.Button(bottom, text='Сохранить JSON', command=self.save_json).pack(side='left', padx=5)

        # Автоматически загружаем книги при старте
        self.load_json(silent=True)

    def _row(self, parent, row, text, var):
        ttk.Label(parent, text=text).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(parent, textvariable=var, width=40).grid(row=row, column=1, padx=5, pady=5, sticky='ew')
        parent.columnconfigure(1, weight=1)

    def validate(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        genre = self.genre_var.get().strip()
        pages = self.pages_var.get().strip()
        if not all([title, author, genre, pages]):
            messagebox.showerror('Ошибка', 'Все поля должны быть заполнены.')
            return None
        if not pages.isdigit():
            messagebox.showerror('Ошибка', 'Количество страниц должно быть числом.')
            return None
        return {'title': title, 'author': author, 'genre': genre, 'pages': int(pages)}

    def add_book(self):
        book = self.validate()
        if not book:
            return
        self.books.append(book)
        self.refresh_table()
        self.clear_form()

    def clear_form(self):
        for v in [self.title_var, self.author_var, self.genre_var, self.pages_var]:
            v.set('')

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        genre_filter = self.genre_filter_var.get().strip().casefold()
        pages_text = self.pages_filter_var.get().strip()
        pages_limit = int(pages_text) if pages_text.isdigit() else None
        for book in self.books:
            if genre_filter and genre_filter not in book['genre'].casefold():
                continue
            if pages_limit is not None and book['pages'] <= pages_limit:
                continue
            self.tree.insert('', 'end', values=(
                book['title'], book['author'], book['genre'], book['pages']
            ))

    def reset_filters(self):
        self.genre_filter_var.set('')
        self.pages_filter_var.set('200')
        self.refresh_table()

    def save_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json')],
            initialfile=DATA_FILE
        )
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)
        messagebox.showinfo('Сохранение', f'Данные сохранены в {path}')

    def load_json(self, silent=False):
        path = DATA_FILE
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            self.books = []
            for b in raw:
                self.books.append({
                    'title': b.get('title', ''),
                    'author': b.get('author', ''),
                    'genre': b.get('genre', ''),
                    'pages': b.get('pages', 0)
                })
            self.refresh_table()
            if not silent:
                messagebox.showinfo('Загрузка', f'Данные загружены из {path}')
        except FileNotFoundError:
            if not silent:
                messagebox.showwarning('Загрузка', 'Файл books.json не найден, создана пустая база.')
        except Exception as e:
            if not silent:
                messagebox.showerror('Ошибка', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    BookTrackerApp(root)
    root.mainloop()