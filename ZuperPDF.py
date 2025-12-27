import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image, ImageTk
import os
import io
import time
import datetime
import fitz  

class PDFToolsApp:
    def get_barcode_from_first_file(self):
        try:
            from pyzbar.pyzbar import decode
            from pdf2image import convert_from_path
        except ImportError:
            return None
        if not self.file_list:
            return None
        file_path = self.file_list[0]
        file_type = self.file_types[0]
        barcode = None
        try:
            if file_type == "pdf":
                # Convert first page of PDF to image
                images = convert_from_path(file_path, first_page=1, last_page=1, dpi=200)
                if images:
                    img = images[0]
                    decoded = decode(img)
                    if decoded:
                        barcode = decoded[0].data.decode('utf-8').replace("X", "")
            else:
                img = Image.open(file_path)
                decoded = decode(img)
                if decoded:
                    barcode = decoded[0].data.decode('utf-8').replace("X", "")
        except Exception:
            pass
        return barcode

    def __init__(self, master):
        self.master = master
        self.master.geometry('1200x800')  # Ukuran window cukup untuk semua menu dan area utama
        self.last_input_dir = r"G:\Other computers\My Computer (1)\2025-08-25"
        self.last_output_dir = r"G:\My Drive\Scan Ranap Mesin"
        self.file_list = []
        self.file_types = []
        self.current_preview_page = 1
        self._last_preview_update = 0
        self.preview_zoom = 1.0
        self.preview_rotations = {}  # {(file_index, page): angle}
        self.setup_ui()

    def setup_ui(self):
        self.master.title("Zzuper PDF")

        # --- Add canvas and scrollbar for the main window ---
        self.main_canvas = tk.Canvas(self.master, borderwidth=0)
        self.main_scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame that will be scrolled
        self.main_frame = tk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Update scrollregion when size changes
        def _on_frame_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        self.main_frame.bind("<Configure>", _on_frame_configure)

        # --- All main widgets moved to self.main_frame ---
        self.label_input_dir = tk.Label(self.main_frame, text=f"Lokasi Input: {self.last_input_dir}", anchor="w", fg="blue")
        self.label_input_dir.pack(fill=tk.X, padx=10, pady=(0, 2))
        self.label_output_dir = tk.Label(self.main_frame, text=f"Lokasi Output: {self.last_output_dir}", anchor="w", fg="green")
        self.label_output_dir.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.btn_select_input = tk.Button(self.main_frame, text="Pilih Folder Input", command=self.select_input_dir)
        self.btn_select_input.pack(fill=tk.X, padx=10, pady=(0, 2))
        self.btn_select_output = tk.Button(self.main_frame, text="Pilih Folder Output", command=self.select_output_dir)
        self.btn_select_output.pack(fill=tk.X, padx=10, pady=(0, 10))

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        self.btn_images_and_pdf_to_pdf = tk.Button(btn_frame, text="Gabung Gambar & PDF ke PDF", command=self.images_and_pdf_to_pdf)
        self.btn_images_and_pdf_to_pdf.pack(side=tk.LEFT, padx=5)



        menu_frame = tk.Frame(self.main_frame)
        menu_frame.pack(pady=5)

        self._last_preview_update = 0
        self.preview_zoom = 1.0

        list_frame = tk.Frame(self.main_frame)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", borderwidth=1, relief="solid")
        style.configure("Treeview", rowheight=22, borderwidth=1, relief="solid")
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        self.tree = ttk.Treeview(list_frame, columns=("No", "Nama File"), show="headings", selectmode="browse")
        self.tree.heading("No", text="No", command=lambda: self.treeview_sort_column("No", False))
        self.tree.heading("Nama File", text="Nama File", command=lambda: self.treeview_sort_column("Nama File", False))
        self.tree.column("No", width=25, anchor="center")
        self.tree.column("Nama File", width=230, anchor="w")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.preview_selected_file_side())

        self.preview_frame = tk.Frame(list_frame, bd=2, relief=tk.SUNKEN)
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        # Perbesar canvas preview utama dan buat dinamis
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='white', scrollregion=(0, 0, 800, 1800))
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas.bind("<MouseWheel>", self.on_preview_zoom)
        self.preview_canvas.bind("<Configure>", lambda e: self.preview_selected_file_side())
        self.preview_scrollbar = tk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        self.preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_canvas.config(yscrollcommand=self.preview_scrollbar.set)
        self.preview_info_label = tk.Label(self.preview_frame, text="", font=('Arial', 10, 'bold'))
        self.preview_info_label.pack(pady=5)
        nav_frame = tk.Frame(self.preview_frame)
        nav_frame.pack(pady=2)
        self.btn_prev_page = tk.Button(nav_frame, text="<<", command=self.preview_prev_page)
        self.btn_prev_page.pack(side=tk.LEFT)
        self.btn_next_page = tk.Button(nav_frame, text=">>", command=self.preview_next_page)
        self.btn_next_page.pack(side=tk.LEFT)
        # --- Tambah tombol rotasi dan simpan ---
        rotate_frame = tk.Frame(self.preview_frame)
        rotate_frame.pack(pady=2)
        self.btn_rotate_left = tk.Button(rotate_frame, text="⟲ Kiri", command=lambda: self.rotate_preview(-90))
        self.btn_rotate_left.pack(side=tk.LEFT, padx=2)
        self.btn_rotate_right = tk.Button(rotate_frame, text="Kanan ⟳", command=lambda: self.rotate_preview(90))
        self.btn_rotate_right.pack(side=tk.LEFT, padx=2)
        self.btn_rotate_up = tk.Button(rotate_frame, text="Atas", command=lambda: self.rotate_preview(180))
        self.btn_rotate_up.pack(side=tk.LEFT, padx=2)
        self.btn_rotate_down = tk.Button(rotate_frame, text="Bawah", command=lambda: self.rotate_preview(0))
        self.btn_rotate_down.pack(side=tk.LEFT, padx=2)
        self.btn_save_rotated = tk.Button(rotate_frame, text="Simpan Rotasi", command=self.save_rotated_preview)
        self.btn_save_rotated.pack(side=tk.LEFT, padx=2)
        self._rotated_img = None
        self._rotated_pdf_page = None

        order_btn_frame = tk.Frame(list_frame)
        order_btn_frame.pack(side=tk.LEFT, padx=5)
        self.btn_move_up = tk.Button(order_btn_frame, text="↑", command=self.move_up)
        self.btn_move_up.pack(pady=5)
        self.btn_move_down = tk.Button(order_btn_frame, text="↓", command=self.move_down)
        self.btn_move_down.pack(pady=5)

        file_btn_frame = tk.Frame(self.main_frame)
        file_btn_frame.pack(pady=5)
        self.btn_add_pdf = tk.Button(file_btn_frame, text="Tambah PDF", command=lambda: self.add_files("pdf"))
        self.btn_add_pdf.pack(side=tk.LEFT, padx=5)
        self.btn_add_image = tk.Button(file_btn_frame, text="Tambah Gambar", command=lambda: self.add_files("image"))
        self.btn_add_image.pack(side=tk.LEFT, padx=5)
        self.btn_remove_file = tk.Button(file_btn_frame, text="Hapus File Terpilih", command=self.remove_file)
        self.btn_remove_file.pack(side=tk.LEFT, padx=5)
        # Hapus tombol Sisipkan di Posisi
        # self.btn_insert_at = tk.Button(file_btn_frame, text="Sisipkan di Posisi", command=self.insert_at_position)
        # self.btn_insert_at.pack(side=tk.LEFT, padx=5)
        self.btn_refresh = tk.Button(file_btn_frame, text="Refresh (Kosongkan Daftar)", command=self.refresh_file_list)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

    def select_input_dir(self):
        folder = filedialog.askdirectory(title="Pilih Folder Input", initialdir=self.last_input_dir)
        if folder:
            self.last_input_dir = folder
            self.update_dir_labels()

    def select_output_dir(self):
        folder = filedialog.askdirectory(title="Pilih Folder Output", initialdir=self.last_output_dir)
        if folder:
            self.last_output_dir = folder
            self.update_dir_labels()

    def update_dir_labels(self):
        self.label_input_dir.config(text=f"Lokasi Input: {self.last_input_dir}")
        self.label_output_dir.config(text=f"Lokasi Output: {self.last_output_dir}")

    def on_preview_zoom(self, event):
        if hasattr(event, 'delta'):
            if event.delta > 0:
                self.preview_zoom *= 1.1
            else:
                self.preview_zoom /= 1.1
        elif hasattr(event, 'num'):
            if event.num == 4:
                self.preview_zoom *= 1.1
            elif event.num == 5:
                self.preview_zoom /= 1.1
        self.preview_zoom = max(0.2, min(self.preview_zoom, 5.0))
        self.preview_selected_file_side()

    def refresh_file_list(self):
        if messagebox.askyesno("Konfirmasi", "Kosongkan daftar file yang sudah dipilih?"):
            self.file_list.clear()
            self.file_types.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.preview_canvas.delete("all")
            self.preview_info_label.config(text="")

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def rotate_preview(self, angle):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        file_type = self.file_types[index]
        page = self.current_preview_page if file_type == "pdf" else None
        key = (index, page)
        prev_angle = self.preview_rotations.get(key, 0)
        new_angle = (prev_angle + angle) % 360
        self.preview_rotations[key] = new_angle
        self.preview_selected_file_side()

    def preview_selected_file_side(self):
        now = time.time()
        if hasattr(self, "_last_preview_update") and now - self._last_preview_update < 0.1:
            return
        self._last_preview_update = now
        selected = self.tree.selection()
        if not selected:
            self.preview_canvas.delete("all")
            self.preview_info_label.config(text="")
            self.current_preview_page = 1
            self._rotated_img = None
            self._rotated_pdf_page = None
            return
        index = self.tree.index(selected[0])
        file_path = self.file_list[index]
        file_type = self.file_types[index]
        self.preview_canvas.delete("all")
        info_text = f"File ke-{index+1} dari {len(self.file_list)}: {os.path.basename(file_path)}"
        a5_width, a5_height = 420, 595
        try:
            self.preview_canvas.update_idletasks()
            margin = 1
            page = self.current_preview_page if file_type == "pdf" else None
            key = (index, page)
            angle = self.preview_rotations.get(key, 0)
            rotasi = angle % 360
            if file_type == "pdf":
                doc = fitz.open(file_path)
                total_pages = doc.page_count
                if not hasattr(self, "current_preview_page") or self.current_preview_page < 1:
                    self.current_preview_page = 1
                if self.current_preview_page > total_pages:
                    self.current_preview_page = total_pages
                page_idx = self.current_preview_page - 1
                page_obj = doc.load_page(page_idx)
                pix = page_obj.get_pixmap(matrix=fitz.Matrix(1, 1))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                if rotasi == 0:
                    pass
                elif rotasi == 90:
                    img = img.rotate(90, expand=True)
                elif rotasi == 180:
                    img = img.rotate(180, expand=True)
                elif rotasi == 270:
                    img = img.rotate(270, expand=True)
                img_w, img_h = img.size
                scale = min(a5_width / img_w, a5_height / img_h, 1.0) * self.preview_zoom
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                self._preview_imgs = [photo]
                x_center = a5_width // 2
                y_center = a5_height // 2
                self.preview_canvas.config(width=a5_width, height=a5_height, scrollregion=(0, 0, a5_width, a5_height))
                self.preview_canvas.create_image(x_center, y_center, image=photo, anchor="center")
                info_text += f" | Halaman {self.current_preview_page} dari {total_pages}"
                self._rotated_img = img
                self._rotated_pdf_page = page_obj
        except Exception as e:
            self.preview_canvas.create_text(a5_width//2, a5_height//2, text=f"Preview gagal:\n{e}", fill="red")
        if file_type == "image":
            try:
                img = Image.open(file_path)
                key = (index, None)
                angle = self.preview_rotations.get(key, 0)
                rotasi = angle % 360
                if rotasi == 0:
                    pass
                elif rotasi == 90:
                    img = img.rotate(90, expand=True)
                elif rotasi == 180:
                    img = img.rotate(180, expand=True)
                elif rotasi == 270:
                    img = img.rotate(270, expand=True)
                scale = min(a5_width / img.width, a5_height / img.height, 1.0) * self.preview_zoom
                new_w = int(img.width * scale)
                new_h = int(img.height * scale)
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                self._preview_imgs = [photo]
                x_center = a5_width // 2
                y_center = a5_height // 2
                self.preview_canvas.config(width=a5_width, height=a5_height, scrollregion=(0, 0, a5_width, a5_height))
                self.preview_canvas.create_image(x_center, y_center, image=photo, anchor="center")
                info_text += f" | Gambar: {img.width}x{img.height}px"
                self._rotated_img = img
                self._rotated_pdf_page = None
            except Exception as e:
                self.preview_canvas.create_text(a5_width//2, a5_height//2, text=f"Preview gagal:\n{e}", fill="red")
        self.preview_info_label.config(text=info_text)

    def preview_next_page(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        file_path = self.file_list[index]
        file_type = self.file_types[index]
        if file_type == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            max_per_grid = 4
            sisa = total_pages - self.current_preview_page
            if sisa >= max_per_grid:
                self.current_preview_page += max_per_grid
            elif sisa > 0:
                self.current_preview_page += sisa
            else:
                self.current_preview_page = total_pages
            self.preview_selected_file_side()

    def preview_prev_page(self):
        pages_per_grid = 4
        if self.current_preview_page > pages_per_grid:
            self.current_preview_page -= pages_per_grid
        else:
            self.current_preview_page = 1
        self.preview_selected_file_side()

    def add_files(self, file_type):
        if file_type == "pdf":
            files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")], title="Pilih file PDF", initialdir=self.last_input_dir)
            file_type_str = "pdf"
        else:
            files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")], title="Pilih file gambar", initialdir=self.last_input_dir)
            file_type_str = "image"
        if files:
            self.last_input_dir = os.path.dirname(files[0])
            self.update_dir_labels()
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
                    self.file_types.append(file_type_str)
                    self.tree.insert("", "end", values=(len(self.file_list), os.path.basename(f)))
            if self.file_list:
                for item in self.tree.selection():
                    self.tree.selection_remove(item)
                last = self.tree.get_children()[-1]
                self.tree.selection_set(last)
                self.tree.see(last)
                self.preview_selected_file_side()

    def remove_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item[0])
            self.file_list.pop(index)
            self.file_types.pop(index)
            self.tree.delete(selected_item[0])
            for idx, item in enumerate(self.tree.get_children(), start=1):
                self.tree.item(item, values=(idx, os.path.basename(self.file_list[idx-1])))

    def move_up(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item[0])
            if index > 0:
                self.file_list[index], self.file_list[index-1] = self.file_list[index-1], self.file_list[index]
                self.file_types[index], self.file_types[index-1] = self.file_types[index-1], self.file_types[index]
                above_item = self.tree.get_children()[index-1]
                current_values = self.tree.item(selected_item[0], "values")
                above_values = self.tree.item(above_item, "values")
                self.tree.item(selected_item[0], values=above_values)
                self.tree.item(above_item, values=current_values)
                self.tree.selection_set(above_item)
                self.tree.see(above_item)
                for idx, item in enumerate(self.tree.get_children(), start=1):
                    self.tree.item(item, values=(idx, os.path.basename(self.file_list[idx-1])))

    def move_down(self):
        selected_item = self.tree.selection()
        items = self.tree.get_children()
        if selected_item:
            index = self.tree.index(selected_item[0])
            if index < len(items) - 1:
                self.file_list[index], self.file_list[index+1] = self.file_list[index+1], self.file_list[index]
                self.file_types[index], self.file_types[index+1] = self.file_types[index+1], self.file_types[index]
                below_item = items[index+1]
                current_values = self.tree.item(selected_item[0], "values")
                below_values = self.tree.item(below_item, "values")
                self.tree.item(selected_item[0], values=below_values)
                self.tree.item(below_item, values=current_values)
                self.tree.selection_set(below_item)
                self.tree.see(below_item)
                for idx, item in enumerate(self.tree.get_children(), start=1):
                    self.tree.item(item, values=(idx, os.path.basename(self.file_list[idx-1])))

    def get_effective_file(self, index):
        file_path = self.file_list[index]
        file_type = self.file_types[index]
        page = self.current_preview_page if file_type == "pdf" else None
        key = (index, page)
        angle = self.preview_rotations.get(key, 0)
        rotasi = angle % 360
        if rotasi == 0:
            return file_path
        # Untuk proses utama, langsung gunakan objek gambar hasil rotasi tanpa file temp
        if file_type == "image":
            img = Image.open(file_path)
            if rotasi == 90:
                img = img.rotate(90, expand=True)
            elif rotasi == 180:
                img = img.rotate(180, expand=True)
            elif rotasi == 270:
                img = img.rotate(270, expand=True)
            return img  # Kembalikan objek PIL.Image
        elif file_type == "pdf":
            doc = fitz.open(file_path)
            page_num = self.current_preview_page - 1 if hasattr(self, "current_preview_page") else 0
            page_obj = doc.load_page(page_num)
            pix = page_obj.get_pixmap(matrix=fitz.Matrix(1, 1))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            if rotasi == 90:
                img = img.rotate(90, expand=True)
            elif rotasi == 180:
                img = img.rotate(180, expand=True)
            elif rotasi == 270:
                img = img.rotate(270, expand=True)
            return img  # Kembalikan objek PIL.Image
        return file_path

    def merge_pdf(self):
        if not self.file_list:
            messagebox.showwarning("Peringatan", "Silakan tambahkan file terlebih dahulu.")
            return
        # Barcode as default filename if found
        barcode_name = self.get_barcode_from_first_file()
        if barcode_name:
            default_name = f"{barcode_name}.pdf"
            messagebox.showinfo("Barcode Ditemukan", f"Barcode terdeteksi: {barcode_name}\nNama file default akan menggunakan barcode.")
        else:
            default_name = datetime.datetime.now().strftime("Scan_%Y%m%d_%H%M%S.pdf")
            messagebox.showinfo("Barcode Tidak Ditemukan", "Barcode tidak ditemukan pada file pertama. Nama file default tetap Scan_...")
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Simpan PDF Gabungan",
            initialdir=self.last_output_dir,
            initialfile=default_name
        )
        if save_path:
            self.last_output_dir = os.path.dirname(save_path)
            self.update_dir_labels()
        if not save_path:
            return
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape, portrait
            from reportlab.lib.utils import ImageReader
            PAGE_PORTRAIT = A4
            PAGE_LANDSCAPE = landscape(A4)
            temp_pdf = io.BytesIO()
            c = canvas.Canvas(temp_pdf)
            MAX_DIM = 1200  # px
            for idx, (file_path, file_type) in enumerate(zip(self.file_list, self.file_types)):
                # If this entry is a PDF, render all pages and add each as its own output page
                if file_type == "pdf" or (isinstance(file_path, str) and file_path.lower().endswith('.pdf')):
                    try:
                        doc = fitz.open(file_path)
                        for page_num in range(doc.page_count):
                            page = doc.load_page(page_num)
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                            # Apply any stored rotation for this file/page (preview_rotations keys use 1-based page numbers)
                            angle = self.preview_rotations.get((idx, page_num + 1), 0) % 360
                            if angle == 90:
                                img = img.rotate(90, expand=True)
                            elif angle == 180:
                                img = img.rotate(180, expand=True)
                            elif angle == 270:
                                img = img.rotate(270, expand=True)

                            img_w, img_h = img.size
                            # Resize agar lebar/tinggi maksimal MAX_DIM px
                            if img_w > img_h and img_w > MAX_DIM:
                                new_w = MAX_DIM
                                new_h = int(img_h * (MAX_DIM / img_w))
                                img = img.resize((new_w, new_h), Image.LANCZOS)
                            elif img_h >= img_w and img_h > MAX_DIM:
                                new_h = MAX_DIM
                                new_w = int(img_w * (MAX_DIM / img_h))
                                img = img.resize((new_w, new_h), Image.LANCZOS)
                            img_w, img_h = img.size

                            # Pilih orientasi halaman
                            if img_w > img_h:
                                page_size = PAGE_LANDSCAPE
                            else:
                                page_size = PAGE_PORTRAIT
                            c.setPageSize(page_size)
                            pw, ph = page_size
                            # Scaling agar gambar fit ke halaman (tanpa crop, proporsional)
                            scale = min(pw / img_w, ph / img_h)
                            draw_w = img_w * scale
                            draw_h = img_h * scale
                            x = (pw - draw_w) / 2
                            y = (ph - draw_h) / 2
                            # Simpan ke buffer JPEG terkompresi
                            img_buf = io.BytesIO()
                            img.save(img_buf, format='JPEG', quality=80, optimize=True)
                            img_buf.seek(0)
                            c.drawImage(ImageReader(img_buf), x, y, width=draw_w, height=draw_h)
                            c.showPage()
                    finally:
                        try:
                            doc.close()
                        except Exception:
                            pass
                else:
                    # Single image (may be a PIL.Image returned by get_effective_file if rotated)
                    effective = self.get_effective_file(idx)
                    if isinstance(effective, Image.Image):
                        img = effective.convert('RGB')
                    else:
                        img = Image.open(effective).convert('RGB')

                    img_w, img_h = img.size
                    # Resize agar lebar/tinggi maksimal MAX_DIM px
                    if img_w > img_h and img_w > MAX_DIM:
                        new_w = MAX_DIM
                        new_h = int(img_h * (MAX_DIM / img_w))
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                    elif img_h >= img_w and img_h > MAX_DIM:
                        new_h = MAX_DIM
                        new_w = int(img_w * (MAX_DIM / img_h))
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                    img_w, img_h = img.size

                    # Pilih orientasi halaman
                    if img_w > img_h:
                        page_size = PAGE_LANDSCAPE
                    else:
                        page_size = PAGE_PORTRAIT
                    c.setPageSize(page_size)
                    pw, ph = page_size
                    # Scaling agar gambar fit ke halaman (tanpa crop, proporsional)
                    scale = min(pw / img_w, ph / img_h)
                    draw_w = img_w * scale
                    draw_h = img_h * scale
                    x = (pw - draw_w) / 2
                    y = (ph - draw_h) / 2
                    # Simpan ke buffer JPEG terkompresi
                    img_buf = io.BytesIO()
                    img.save(img_buf, format='JPEG', quality=80, optimize=True)
                    img_buf.seek(0)
                    c.drawImage(ImageReader(img_buf), x, y, width=draw_w, height=draw_h)
                    c.showPage()
                img_w, img_h = img.size
                # Resize agar lebar/tinggi maksimal MAX_DIM px
                if img_w > img_h and img_w > MAX_DIM:
                    new_w = MAX_DIM
                    new_h = int(img_h * (MAX_DIM / img_w))
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                elif img_h >= img_w and img_h > MAX_DIM:
                    new_h = MAX_DIM
                    new_w = int(img_w * (MAX_DIM / img_h))
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                img_w, img_h = img.size
                # Pilih orientasi halaman
                if img_w > img_h:
                    page_size = PAGE_LANDSCAPE
                else:
                    page_size = PAGE_PORTRAIT
                c.setPageSize(page_size)
                pw, ph = page_size
                # Scaling agar gambar fit ke halaman (tanpa crop, proporsional)
                scale = min(pw / img_w, ph / img_h)
                draw_w = img_w * scale
                draw_h = img_h * scale
                x = (pw - draw_w) / 2
                y = (ph - draw_h) / 2
                # Simpan ke buffer JPEG terkompresi
                img_buf = io.BytesIO()
                img.save(img_buf, format='JPEG', quality=80, optimize=True)
                img_buf.seek(0)
                c.drawImage(ImageReader(img_buf), x, y, width=draw_w, height=draw_h)
                c.showPage()
            c.save()
            temp_pdf.seek(0)
            reader = PdfReader(temp_pdf)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(save_path, "wb") as output_pdf:
                writer.write(output_pdf)
            messagebox.showinfo("Sukses", f"File berhasil digabung:\n{save_path}")

            # Offer to delete physical files
            if messagebox.askyesno("Hapus File?", "Apakah ingin menghapus file sumber dari komputer?"):
                gagal = []
                for f in self.file_list:
                    try:
                        os.remove(f)
                    except Exception as e:
                        gagal.append(f"{f} ({e})")
                if gagal:
                    messagebox.showwarning("Peringatan", f"Sebagian file gagal dihapus:\n" + "\n".join(gagal))
                else:
                    messagebox.showinfo("Info", "Semua file sumber berhasil dihapus.")

                self.file_list.clear()
                self.file_types.clear()
                self.tree.delete(0, tk.END)

        except Exception as e:
            print(f"Gagal menggabung file: {e}")  # hanya tampil di terminal, tidak pop-up

    def images_and_pdf_to_pdf(self):
        self.merge_pdf()


    def organize_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih file PDF dari daftar!")
            return
        index = self.tree.index(selected[0])
        file_path = self.file_list[index]
        file_type = self.file_types[index]
        if file_type != "pdf":
            messagebox.showwarning("Peringatan", "File yang dipilih bukan PDF!")
            return
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            org_window = tk.Toplevel(self.master)
            org_window.title("Atur PDF")
            org_window.geometry("900x700")
            main_frame = tk.Frame(org_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            list_preview_frame = tk.Frame(main_frame)
            list_preview_frame.pack(fill=tk.BOTH, expand=True)
            list_frame = tk.Frame(list_preview_frame)
            list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
            tk.Label(list_frame, text="Daftar Halaman", font=('Arial', 10, 'bold')).pack()
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            pages_listbox = tk.Listbox(
                list_frame, 
                selectmode=tk.SINGLE,
                yscrollcommand=scrollbar.set,
                width=30,
                height=25
            )
            pages_listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=pages_listbox.yview)
            pages_listbox.bind('<<ListboxSelect>>', lambda e: self.show_page_preview(org_window))
            nav_frame = tk.Frame(main_frame)
            nav_frame.pack(pady=2)
            btn_prev = tk.Button(nav_frame, text="<<", command=lambda: self.go_prev_page(pages_listbox))
            btn_prev.pack(side=tk.LEFT)
            btn_next = tk.Button(nav_frame, text=">>", command=lambda: self.go_next_page(pages_listbox))
            btn_next.pack(side=tk.LEFT)
            preview_frame = tk.Frame(list_preview_frame, bd=2, relief=tk.SUNKEN)
            preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            tk.Label(preview_frame, text="Preview Halaman", font=('Arial', 10, 'bold')).pack()
            preview_canvas = tk.Canvas(preview_frame, bg='white', scrollregion=(0, 0, 800, 1800))
            preview_canvas.pack(fill=tk.BOTH, expand=True, pady=5)
            # Define zoom handler for Atur PDF preview
            org_window.preview_zoom = 1.0
            def on_org_preview_zoom(event):
                if hasattr(event, 'delta'):
                    if event.delta > 0:
                        org_window.preview_zoom *= 1.1
                    else:
                        org_window.preview_zoom /= 1.1
                elif hasattr(event, 'num'):
                    if event.num == 4:
                        org_window.preview_zoom *= 1.1
                    elif event.num == 5:
                        org_window.preview_zoom /= 1.1
                org_window.preview_zoom = max(0.2, min(org_window.preview_zoom, 5.0))
                self.show_page_preview(org_window)
            preview_canvas.bind("<MouseWheel>", on_org_preview_zoom)
            page_info_label = tk.Label(preview_frame, text="Pilih halaman untuk melihat preview", font=('Arial', 9))
            page_info_label.pack()
            # Tambah tombol rotasi preview di Atur PDF
            rotate_frame = tk.Frame(preview_frame)
            rotate_frame.pack(pady=2)
            def rotate_org_preview(angle):
                selected = org_window.pages_listbox.curselection()
                if not selected:
                    return
                index = selected[0]
                item = org_window.pages_listbox.get(index)
                # Pastikan ini adalah halaman PDF asli
                if not item.startswith("Halaman"):
                    return
                # Simpan info rotasi di listbox
                current_text = org_window.pages_listbox.get(index)
                if " (Diputar" in current_text:
                    base_text = current_text.split(" (Diputar")[0]
                else:
                    base_text = current_text
                if angle == 0:
                    rot_label = "Bawah"
                    degrees = 0
                elif angle == 180:
                    rot_label = "Atas"
                    degrees = 180
                elif angle == -90:
                    rot_label = "Kiri"
                    degrees = -90
                else:
                    rot_label = "Kanan"
                    degrees = 90
                org_window.pages_listbox.delete(index)
                org_window.pages_listbox.insert(index, f"{base_text} (Diputar {rot_label})")
                org_window.pages_listbox.select_set(index)
                # Simpan info rotasi di org_window
                if not hasattr(org_window, 'rotations'):
                    org_window.rotations = {}
                org_window.rotations[index] = degrees
                self.show_page_preview(org_window)
            btn_left = tk.Button(rotate_frame, text="⟲ Kanan", command=lambda: rotate_org_preview(-90))
            btn_left.pack(side=tk.LEFT, padx=2)
            btn_right = tk.Button(rotate_frame, text="Kiri ⟳", command=lambda: rotate_org_preview(90))
            btn_right.pack(side=tk.LEFT, padx=2)
            btn_up = tk.Button(rotate_frame, text="Atas", command=lambda: rotate_org_preview(180))
            btn_up.pack(side=tk.LEFT, padx=2)
            btn_down = tk.Button(rotate_frame, text="Bawah", command=lambda: rotate_org_preview(0))
            btn_down.pack(side=tk.LEFT, padx=2)
            # Tambahkan frame untuk tombol simpan PDF
            save_frame = tk.Frame(main_frame)
            save_frame.pack(pady=10)
            tk.Button(save_frame, text="Simpan PDF", command=lambda: self.save_organized_pdf(org_window)).pack()
            # ...hilangkan referensi org_window dan preview_canvas lokal...
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka PDF:\n{e}")

    def open_rename_barcode_window(self):
        win = tk.Toplevel(self.master)
        win.title("Rename PDF Berdasarkan Barcode")
        win.geometry("600x450")

        frame = tk.Frame(win)
        frame.pack(pady=10)

        log_text = tk.Text(win, height=18, width=70)
        log_text.pack(padx=10, pady=10)

        def read_barcode_from_pdf(pdf_path):
            try:
                from pdf2image import convert_from_path
                from pyzbar.pyzbar import decode
                images = convert_from_path(pdf_path, dpi=300)
                for image in images:
                    decoded_objects = decode(image)
                    if decoded_objects:
                        barcode = decoded_objects[0].data.decode('utf-8').replace("X", "")
                        return barcode
            except Exception as e:
                print(f"Error membaca {pdf_path}: {e}")
            return None

        def rename_pdf_with_barcode(pdf_path):
            barcode_text = read_barcode_from_pdf(pdf_path)
            if barcode_text:
                dir_name = os.path.dirname(pdf_path)
                ext = os.path.splitext(pdf_path)[1]
                new_path = os.path.join(dir_name, f"{barcode_text}{ext}")
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(dir_name, f"{barcode_text}_{counter}{ext}")
                    counter += 1
                os.rename(pdf_path, new_path)
                return f"[OK] {os.path.basename(pdf_path)} → {os.path.basename(new_path)}"
            else:
                return f"[X] Tidak ada barcode di {os.path.basename(pdf_path)}"

        def process_multiple_files():
            files_selected = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
            if files_selected:
                log_text.delete(1.0, tk.END)
                for file_selected in files_selected:
                    result = rename_pdf_with_barcode(file_selected)
                    log_text.insert(tk.END, result + "\n")
                log_text.insert(tk.END, "\nSelesai memproses semua file PDF.")
            else:
                messagebox.showwarning("Peringatan", "File belum dipilih.")

        def batch_rename_pdfs(folder_path):
            log_text.delete(1.0, tk.END)
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(".pdf"):
                    pdf_path = os.path.join(folder_path, file_name)
                    result = rename_pdf_with_barcode(pdf_path)
                    log_text.insert(tk.END, result + "\n")
            log_text.insert(tk.END, "\nSelesai memproses semua file PDF.")

        def pilih_folder():
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                batch_rename_pdfs(folder_selected)
            else:
                messagebox.showwarning("Peringatan", "Folder belum dipilih.")

        btn_pilih_files = tk.Button(frame, text="Pilih Banyak File PDF", command=process_multiple_files, width=20)
        btn_pilih_files.grid(row=0, column=0, padx=5)
        btn_pilih_folder = tk.Button(frame, text="Pilih Folder PDF", command=pilih_folder, width=20)
        btn_pilih_folder.grid(row=0, column=1, padx=5)

    def show_page_preview(self, org_window):
        selected = org_window.pages_listbox.curselection()
        if not selected:
            return
        index = selected[0]
        item = org_window.pages_listbox.get(index)
        max_width, max_height = 1191, 1684
        zoom = getattr(org_window, 'preview_zoom', 1.0)
        canvas_width = org_window.preview_canvas.winfo_width()
        canvas_height = org_window.preview_canvas.winfo_height()
        preview_width = min(canvas_width, max_width)
        preview_height = min(canvas_height, max_height)
        # Preview halaman asli PDF
        if item.startswith("Halaman"):
            page_num = int(item.split()[1]) - 1
            try:
                doc = fitz.open(org_window.current_pdf)
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # Cek rotasi
                degrees = 0
                if hasattr(org_window, 'rotations') and index in org_window.rotations:
                    degrees = org_window.rotations[index]
                if degrees == 0:
                    pass
                elif degrees == 180:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif degrees == -90:
                    img = img.rotate(-90, expand=True)
                elif degrees == 90:
                    img = img.rotate(90, expand=True)
                img_w, img_h = img.size
                scale = min(preview_width / img_w, preview_height / img_h, 1.0) * zoom
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                org_window.preview_canvas.delete("all")
                x_center = preview_width // 2
                y_center = preview_height // 2
                org_window.preview_canvas.create_image(
                    x_center,
                    y_center,
                    image=photo,
                    anchor=tk.CENTER
                )
                org_window.page_info_label.config(text=f"Halaman {page_num+1} dari {doc.page_count}")
                org_window.current_preview_image = photo
            except Exception as e:
                org_window.preview_canvas.delete("all")
                org_window.preview_canvas.create_text(
                    preview_width // 2,
                    preview_height // 2,
                    text=f"Error: {str(e)}",
                    anchor=tk.CENTER,
                    fill="red"
                )
        # Preview file sisipan
        elif "||" in item:
            label, file_path = item.split("||", 1)
            if label.startswith("[Sisipan Gambar]"):
                try:
                    img = Image.open(file_path)
                    img_w, img_h = img.size
                    scale = min(preview_width / img_w, preview_height / img_h, 1.0) * zoom
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img_resized)
                    org_window.preview_canvas.delete("all")
                    x_center = preview_width // 2
                    y_center = preview_height // 2
                    org_window.preview_canvas.create_image(
                        x_center,
                        y_center,
                        image=photo,
                        anchor=tk.CENTER
                    )
                    org_window.page_info_label.config(text=f"Gambar: {os.path.basename(file_path)}")
                    org_window.current_preview_image = photo
                except Exception as e:
                    org_window.preview_canvas.delete("all")
                    org_window.preview_canvas.create_text(
                        preview_width // 2,
                        preview_height // 2,
                        text=f"Error: {str(e)}",
                        anchor=tk.CENTER,
                        fill="red"
                    )
            elif label.startswith("[Sisipan PDF]"):
                try:
                    doc = fitz.open(file_path)
                    page = doc.load_page(0)
                    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img_w, img_h = img.size
                    scale = min(preview_width / img_w, preview_height / img_h, 1.0) * zoom
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img_resized)
                    org_window.preview_canvas.delete("all")
                    x_center = preview_width // 2
                    y_center = preview_height // 2
                    org_window.preview_canvas.create_image(
                        x_center,
                        y_center,
                        image=photo,
                        anchor=tk.CENTER
                    )
                    org_window.page_info_label.config(text=f"PDF: {os.path.basename(file_path)} (Halaman 1)")
                    org_window.current_preview_image = photo
                except Exception as e:
                    org_window.preview_canvas.delete("all")
                    org_window.preview_canvas.create_text(
                        preview_width // 2,
                        preview_height // 2,
                        text=f"Error: {str(e)}",
                        anchor=tk.CENTER,
                        fill="red"
                    )
            else:
                org_window.preview_canvas.delete("all")
                org_window.preview_canvas.create_text(
                    preview_width // 2,
                    preview_height // 2,
                    text="Preview tidak didukung untuk file ini",
                    anchor=tk.CENTER,
                    fill="gray"
                )
    
    def move_page(self, listbox, direction):
        """Memindahkan halaman ke atas atau ke bawah"""
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("Peringatan", "Silakan pilih halaman yang akan dipindahkan")
            return
        index = selected[0]
        if direction == "up" and index > 0:
            # Pindah ke atas
            item = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index-1, item)
            listbox.select_set(index-1)
        elif direction == "down" and index < listbox.size()-1:
            # Pindah ke bawah
            item = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index+1, item)
            listbox.select_set(index+1)
    
    def delete_page(self, listbox):
        """Menghapus halaman yang dipilih"""
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("Peringatan", "Silakan pilih halaman yang akan dihapus")
            return
        index = selected[0]
        listbox.delete(index)
    
    def rotate_page(self, org_window):
        """Memutar halaman yang dipilih dengan preview"""
        selected = org_window.pages_listbox.curselection()
        if not selected:
            messagebox.showwarning("Peringatan", "Silakan pilih halaman yang akan diputar")
            return
            
        index = selected[0]
        item = org_window.pages_listbox.get(index)
        
        # Pastikan ini adalah halaman PDF asli
        if not item.startswith("Halaman"):
            messagebox.showwarning("Peringatan", "Hanya bisa memutar halaman PDF asli")
            return
            
        # Tanyakan derajat rotasi
        degrees = simpledialog.askinteger(
            "Putar Halaman",
            "Masukkan derajat rotasi (90, 180, atau 270):",
            minvalue=90,
            maxvalue=270,
            initialvalue=90
        )
        
        if degrees is None or degrees not in [90, 180, 270]:
            messagebox.showerror("Error", "Derajat rotasi harus 90, 180, atau 270")
            return
            
        # Update label di listbox untuk menandakan halaman telah diputar
        current_text = org_window.pages_listbox.get(index)
        
        # Hapus keterangan rotasi sebelumnya jika ada
        if " (Diputar" in current_text:
            base_text = current_text.split(" (Diputar")[0]
        else:
            base_text = current_text
            
        org_window.pages_listbox.delete(index)
        org_window.pages_listbox.insert(index, f"{base_text} (Diputar {degrees}°)")
        org_window.pages_listbox.select_set(index)
        
        # Update preview
        self.show_page_preview(org_window)
    
    def insert_to_pdf(self, listbox):
        """Menyisipkan PDF atau gambar ke dalam PDF yang sedang diatur"""
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("Peringatan", "Silakan pilih posisi untuk menyisipkan")
            return

        index = selected[0]

        # Pilihan jenis file dengan dialog klik, bukan ketik
        file_type = None
        def set_pdf():
            nonlocal file_type
            file_type = "pdf"
            select_win.destroy()
        def set_image():
            nonlocal file_type
            file_type = "image"
            select_win.destroy()
        select_win = tk.Toplevel(self.master)
        select_win.title("Pilih Jenis File")
        tk.Label(select_win, text="Pilih jenis file yang akan disisipkan:").pack(padx=10, pady=10)
        btn_pdf = tk.Button(select_win, text="PDF", command=set_pdf)
        btn_pdf.pack(side=tk.LEFT, padx=10, pady=10)
        btn_img = tk.Button(select_win, text="Gambar", command=set_image)
        btn_img.pack(side=tk.LEFT, padx=10, pady=10)
        select_win.wait_window()
        if file_type not in ["pdf", "image"]:
            return
        if file_type == "pdf":
            files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")], title="Pilih file PDF")
        else:
            files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")], title="Pilih file gambar")

        # Sisipkan file pada posisi yang dipilih
        for f in files:
            nama_file = os.path.basename(f)
            if file_type == "pdf":
                label = f"[Sisipan PDF] {nama_file}"
            else:
                label = f"[Sisipan Gambar] {nama_file}"
            # Simpan path asli sebagai value, label sebagai tampilan
            listbox.insert(index, f"{label}||{f}")
            index += 1
    
    def save_organized_pdf(self, org_window):
        """Menyimpan PDF yang telah diatur"""
        try:
            writer = PdfWriter()
            for i in range(org_window.pages_listbox.size()):
                item = org_window.pages_listbox.get(i)
                # Pisahkan label dan path
                if "||" in item:
                    label, file_path = item.split("||", 1)
                    if label.startswith("[Sisipan Gambar]"):
                        img = Image.open(file_path)
                        img = img.convert('RGB')
                        temp_pdf_path = "temp_pdf_from_image.pdf"
                        img.save(temp_pdf_path)
                        temp_reader = PdfReader(temp_pdf_path)
                        writer.add_page(temp_reader.pages[0])
                        os.remove(temp_pdf_path)
                    elif label.startswith("[Sisipan PDF]"):
                        temp_reader = PdfReader(file_path)
                        for page in temp_reader.pages:
                            writer.add_page(page)
                else:
                    page_num = int(item.split()[1]) - 1
                    if " (Diputar" in item:
                        degrees = int(item.split("Diputar ")[1].replace("°)", ""))
                        page = org_window.reader.pages[page_num]
                        page.rotate(degrees)
                        writer.add_page(page)
                    else:
                        writer.add_page(org_window.reader.pages[page_num])
            now_str = datetime.datetime.now().strftime("Scan_%Y%m%d_%H%M%S.pdf")
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Simpan PDF Hasil Pengaturan",
                initialdir=self.last_output_dir,
                initialfile=now_str
            )
            if save_path:
                self.last_output_dir = os.path.dirname(save_path)
                self.update_dir_labels()
            if not save_path:
                return
            with open(save_path, "wb") as f_out:
                writer.write(f_out)
            messagebox.showinfo("Sukses", f"PDF berhasil diatur dan disimpan:\n{save_path}")
            org_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan PDF:\n{e}")

    def save_rotated_preview(self):
        """Menyimpan hasil rotasi preview ke file baru"""
        selected = self.tree.selection()
        if not selected or self._rotated_img is None:
            messagebox.showwarning("Peringatan", "Tidak ada file yang dipreview atau belum diputar.")
            return
        index = self.tree.index(selected[0])
        file_path = self.file_list[index]
        file_type = self.file_types[index]
        now_str = datetime.datetime.now().strftime("Rotated_%Y%m%d_%H%M%S")
        if file_type == "image":
            ext = os.path.splitext(file_path)[1].lower()
            save_path = filedialog.asksaveasfilename(
                defaultextension=ext,
                filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")],
                title="Simpan Gambar Hasil Rotasi",
                initialdir=self.last_output_dir,
                initialfile=now_str+ext
            )
            if save_path:
                self._rotated_img.save(save_path)
                messagebox.showinfo("Sukses", f"Gambar hasil rotasi berhasil disimpan:\n{save_path}")
        elif file_type == "pdf":
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Simpan PDF Hasil Rotasi",
                initialdir=self.last_output_dir,
                initialfile=now_str+".pdf"
            )
            if save_path:
                img = self._rotated_img.convert('RGB')
                img.save(save_path, "PDF")
                messagebox.showinfo("Sukses", f"Halaman PDF hasil rotasi berhasil disimpan:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolsApp(root)
    root.mainloop()
