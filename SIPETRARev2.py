import pandas as pd
import psycopg2

def connectDB():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="rexec18",
            dbname="sipetra"
        )

        cur = conn.cursor()

        return conn, cur

    except Exception as error:
        print("Koneksi database gagal:", error)
        return None, None


def get_connection():
    """Membuka koneksi database untuk fungsi yang hanya memerlukan koneksi."""
    conn, cur = connectDB()
    if cur is not None:
        cur.close()
    return conn


# =========================================================
# UTILITAS TAMPILAN (STYLING MENU SERAGAM)
# =========================================================

LEBAR_MENU = 40

# Nilai enum untuk kolom Transaksi.status_pembayaran
# (tabel Status_pembayaran sudah dihapus)
STATUS_PEMBAYARAN = ["Belum dibayar", "Menunggu konfirmasi", "Lunas"]


def cetak_header(judul):
    """Mencetak judul menu utama dengan bingkai '=' agar seragam."""
    print("\n" + "=" * LEBAR_MENU)
    print(judul.center(LEBAR_MENU))
    print("=" * LEBAR_MENU)


def cetak_subheader(judul):
    """Mencetak judul sub-menu fitur dengan bingkai '-' agar seragam."""
    print("\n" + "-" * LEBAR_MENU)
    print(judul.center(LEBAR_MENU))
    print("-" * LEBAR_MENU)


def register():
    """Mendaftarkan akun pelanggan baru (Role Pengguna)."""
    print("\n" + "=" * LEBAR_MENU)
    print("       REGISTRASI AKUN PELANGGAN".center(LEBAR_MENU))
    print("=" * LEBAR_MENU)

    nama_pengguna = input("Nama       : ").strip()
    email = input("Email      : ").strip()
    no_telepon = input("No. Telepon: ").strip()
    username = input("Username   : ").strip()
    password_ = input("Password   : ").strip()

    if username == "" or password_ == "":
        print("\nUsername dan password wajib diisi!")
        return None

    conn, cur = connectDB()

    if conn is None:
        return None

    try:
        # Role_ID = 3 adalah 'Pengguna' (pelanggan)
        cur.execute(
            """
            INSERT INTO Pengguna
                (email, nama_pengguna, no_telepon, username, password_, is_active, Role_ID)
            VALUES (%s, %s, %s, %s, %s, TRUE, 3);
            """,
            (email, nama_pengguna, no_telepon, username, password_)
        )
        conn.commit()

        print("\nRegistrasi berhasil!")
        print("Selamat datang,", nama_pengguna)
        print("Silakan login menggunakan akun yang baru dibuat.")

        return {
            "id": None,
            "nama": nama_pengguna,
            "username": username,
            "role": "Pengguna"
        }
    except psycopg2.Error as e:
        conn.rollback()
        print("\nRegistrasi gagal!")
        print("Keterangan:", e)
        return None
    finally:
        cur.close()
        conn.close()


def login():
    print("\n" + "=" * LEBAR_MENU)
    print("          LOGIN SIPETRA".center(LEBAR_MENU))
    print("=" * LEBAR_MENU)

    username = input("Masukkan username : ").strip()
    password = input("Masukkan password : ").strip()

    if username == "" or password == "":
        print("\nUsername dan password wajib diisi!")
        return None

    conn, cur = connectDB()

    if conn is None:
        return None

    cursor = None

    try:
        cursor = conn.cursor()

        query = """
            SELECT p.Pengguna_ID,
                   p.nama_pengguna,
                   p.username,
                   p.password_,
                   p.is_active,
                   r.nama_role
            FROM Pengguna p
            JOIN Role_ r ON p.Role_ID = r.Role_ID
            WHERE p.username = %s
        """

        cursor.execute(query, (username,))
        pengguna = cursor.fetchone()

        if pengguna is None:
            print("\nUsername atau password salah!")
            return None

        pengguna_id = pengguna[0]
        nama = pengguna[1]
        username_db = pengguna[2]
        password_db = pengguna[3]
        status = pengguna[4]
        role = pengguna[5]

        if status == False:
            print("\nAkun kamu sedang tidak aktif!")
            return None

        if password != password_db:
            print("\nUsername atau password salah!")
            return None

        print("\nLogin berhasil!")
        print("Selamat datang,", nama)
        print("Role:", role)

        return {
            "id": pengguna_id,
            "nama": nama,
            "username": username_db,
            "role": role
        }
    except psycopg2.Error as e:
        print("\nTerjadi kesalahan saat login!")
        print("Keterangan:", e)

        return None

    finally:
        if cursor is not None:
            cursor.close()

        conn.close()

def logout():
    """
    Mengakhiri sesi login admin.
    """
    print("Berhasil logout.")


def tambah_akun():
    """
    Menambah akun baru (karyawan/admin).
    """
    print("\n--- TAMBAH AKUN ---")
    email = input("Email: ")
    nama_pengguna = input("Nama: ")
    no_telepon = input("No. Telepon: ")
    username = input("Username: ")
    password_ = input("Password: ")

    print("Pilih role: 1) Admin  2) Karyawan")
    pilihan_role = input("Pilihan: ")
    role_id = 1 if pilihan_role == "1" else 2

    conn, cur = connectDB()

    try:
        cur.execute(
            """
            INSERT INTO Pengguna
                (email, nama_pengguna, no_telepon, username, password_, is_active, Role_ID)
            VALUES (%s, %s, %s, %s, %s, TRUE, %s);
            """,
            (email, nama_pengguna, no_telepon, username, password_, role_id)
        )
        conn.commit()
        print("Akun berhasil ditambahkan.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_akun():
    """
    Menampilkan seluruh data akun (admin & karyawan).
    """
    conn, cur = connectDB()
    try:
        cur.execute(
            """
            SELECT p.Pengguna_ID, p.nama_pengguna, p.email, p.no_telepon,
                   p.username, r.nama_role, p.is_active
            FROM Pengguna p
            JOIN Role_ r ON r.Role_ID = p.Role_ID
            WHERE r.nama_role IN ('Admin', 'Karyawan')
            ORDER BY p.Pengguna_ID;
            """
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Nama", "Email", "No Telepon", "Username", "Role", "Aktif"]
        )
        if dataFrame.empty:
            print("Tidak ada data akun")
        else:
            print("\n--- DATA AKUN (ADMIN & KARYAWAN) ---")
            print(dataFrame.to_string(index=False))
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def ubah_akun():
    """
    Mengubah data akun (termasuk status aktif/nonaktif).
    """
    pengguna_id = input("Masukkan ID akun yang ingin diubah: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Pengguna WHERE Pengguna_ID = %s;", (pengguna_id,))
        row = cur.fetchone()
        if row is None:
            print("Akun tidak ditemukan.")
            return

        print("Data saat ini:", row)
        nama_baru = input("Nama baru (kosongkan jika tidak diubah): ")
        no_telepon_baru = input("No. telepon baru (kosongkan jika tidak diubah): ")
        status_baru = input("Status aktif? (y/n, kosongkan jika tidak diubah): ")

        if nama_baru:
            cur.execute(
                "UPDATE Pengguna SET nama_pengguna = %s WHERE Pengguna_ID = %s;",
                (nama_baru, pengguna_id)
            )
        if no_telepon_baru:
            cur.execute(
                "UPDATE Pengguna SET no_telepon = %s WHERE Pengguna_ID = %s;",
                (no_telepon_baru, pengguna_id)
            )
        if status_baru:
            is_active = status_baru.lower() == "y"
            cur.execute(
                "UPDATE Pengguna SET is_active = %s WHERE Pengguna_ID = %s;",
                (is_active, pengguna_id)
            )

        conn.commit()
        print("Akun berhasil diperbarui.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# B. FITUR PRODUK
# =========================================================

def tambah_produk():
    """
    Menambah data produk baru.
    Catatan: berdasarkan studi kasus, produk hanya 1 (Tembakau Rajangan),
    jadi fitur ini kemungkinan hanya dipakai sekali di awal setup sistem.
    """
    nama_produk = input("Nama produk: ")
    harga = input("Harga per gram: ")
    jumlah = input("Jumlah stok awal (gram): ")
    deskripsi = input("Deskripsi: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Produk (nama_produk, harga, jumlah, deskripsi, is_active)
            VALUES (%s, %s, %s, %s, TRUE);
            """,
            (nama_produk, harga, jumlah, deskripsi)
        )
        conn.commit()
        print("Produk berhasil ditambahkan.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_produk():
    """
    Menampilkan seluruh data produk tembakau yang masih aktif menggunakan pandas DataFrame.
    Dipakai oleh menu admin, kasir, dan pelanggan.
    """
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT Produk_ID, nama_produk, harga, jumlah, deskripsi
            FROM Produk
            WHERE is_active = TRUE
            ORDER BY Produk_ID ASC;
            """
        )
        rows = cur.fetchall()

        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Nama Produk", "Harga/Gram", "Stok (gram)", "Deskripsi"]
        )

        if dataFrame.empty:
            print("Tidak ada data produk.")
        else:
            print("\n--- KATALOG PRODUK TEMBAKAU ---")
            print(dataFrame.to_string(index=False))

    except Exception as e:
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


def ubah_produk():
    """
    Mengubah data produk (harga, deskripsi, dll).
    """
    produk_id = input("Masukkan ID produk yang ingin diubah: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Produk WHERE Produk_ID = %s;", (produk_id,))
        row = cur.fetchone()
        if row is None:
            print("Produk tidak ditemukan.")
            return

        print("Data saat ini:", row)
        harga_baru = input("Harga baru (kosongkan jika tidak diubah): ")
        deskripsi_baru = input("Deskripsi baru (kosongkan jika tidak diubah): ")

        if harga_baru:
            cur.execute(
                "UPDATE Produk SET harga = %s WHERE Produk_ID = %s;",
                (harga_baru, produk_id)
            )
        if deskripsi_baru:
            cur.execute(
                "UPDATE Produk SET deskripsi = %s WHERE Produk_ID = %s;",
                (deskripsi_baru, produk_id)
            )

        conn.commit()
        print("Produk berhasil diperbarui.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def hapus_produk():
    """
    Menghapus data produk menggunakan metode soft delete.
    """
    produk_id = input("Masukkan ID produk yang ingin dihapus: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Produk SET is_active = FALSE WHERE Produk_ID = %s;",
            (produk_id,)
        )
        conn.commit()
        print("Produk berhasil dihapus (soft delete).")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# C. FITUR STOK
# =========================================================

def tambah_stok():
    """
    Menambah data stok (penambahan/pengeluaran manual).
    """
    print("Pilih tipe: 1) Penambahan  2) Pengeluaran")
    pilihan_tipe = input("Pilihan: ")
    tipe = "Penambahan" if pilihan_tipe == "1" else "Pengeluaran"

    jumlah_stok = input("Jumlah (gram): ")
    produk_id = input("ID Produk: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
            VALUES (%s, %s, CURRENT_DATE, TRUE, %s);
            """,
            (tipe, jumlah_stok, produk_id)
        )

        if tipe == "Penambahan":
            cur.execute(
                "UPDATE Produk SET jumlah = jumlah + %s WHERE Produk_ID = %s;",
                (jumlah_stok, produk_id)
            )
        else:
            cur.execute(
                "UPDATE Produk SET jumlah = jumlah - %s WHERE Produk_ID = %s;",
                (jumlah_stok, produk_id)
            )

        conn.commit()
        print("Stok berhasil ditambahkan.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_stok():
    """
    Menampilkan riwayat data stok (log masuk/keluar).
    """
    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT s.Stok_ID, s.tipe, s.jumlah_stok, s.tanggal_pembaruan, pr.nama_produk
            FROM Stok s
            JOIN Produk pr ON pr.Produk_ID = s.Produk_ID
            ORDER BY s.tanggal_pembaruan DESC;
            """
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tipe", "Jumlah", "Tanggal", "Produk"]
        )
        if dataFrame.empty:
            print("Tidak ada data stok")
        else:
            print("\n--- DATA STOK ---")
            print(dataFrame.to_string(index=False))
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# D. FITUR PRODUK RUSAK
# =========================================================

def tambah_produk_rusak():
    """
    Mencatat laporan produk rusak.
    Membuat 1 baris Stok (pengeluaran) dan 1 baris Produk_rusak sekaligus,
    lalu mengurangi jumlah stok di tabel Produk.
    """
    jumlah_rusak = input("Jumlah produk rusak (gram): ")
    deskripsi = input("Deskripsi/penyebab kerusakan: ")
    produk_id = input("ID Produk: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
            VALUES ('Pengeluaran', %s, CURRENT_DATE, TRUE, %s)
            RETURNING Stok_ID;
            """,
            (jumlah_rusak, produk_id)
        )
        stok_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO Produk_rusak (jumlah_produk, deskripsi, Stok_ID)
            VALUES (%s, %s, %s);
            """,
            (jumlah_rusak, deskripsi, stok_id)
        )

        cur.execute(
            "UPDATE Produk SET jumlah = jumlah - %s WHERE Produk_ID = %s;",
            (jumlah_rusak, produk_id)
        )

        conn.commit()
        print("Laporan produk rusak berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_produk_rusak():
    """
    Menampilkan data laporan produk rusak.
    Tanggal diambil dari Stok karena Produk_rusak berpasangan 1-ke-1 dengan Stok.
    """
    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT pr.Produk_Rusak_ID, s.tanggal_pembaruan, pr.jumlah_produk, pr.deskripsi
            FROM Produk_rusak pr
            JOIN Stok s ON s.Stok_ID = pr.Stok_ID
            ORDER BY s.tanggal_pembaruan DESC;
            """
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Jumlah Rusak", "Deskripsi"]
        )
        if dataFrame.empty:
            print("Tidak ada data produk rusak")
        else:
            print("\n--- DATA PRODUK RUSAK ---")
            print(dataFrame.to_string(index=False))
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# E. FITUR LAHAN
# =========================================================

def tambah_lahan():
    """
    Menambah data lahan.
    """
    nama_lahan = input("Nama lahan: ")
    lokasi = input("Lokasi: ")
    luas_lahan = input("Luas lahan (hektar): ")
    print("Status: 1) Ditanami  2) Kosong")
    pilihan_status = input("Pilihan: ")
    status = "Ditanami" if pilihan_status == "1" else "Kosong"

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Lahan (nama_lahan, lokasi, luas_lahan, status)
            VALUES (%s, %s, %s, %s);
            """,
            (nama_lahan, lokasi, luas_lahan, status)
        )
        conn.commit()
        print("Lahan berhasil ditambahkan.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_lahan():
    """
    Menampilkan data lahan.
    """
    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Lahan;")
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Nama Lahan", "Lokasi", "Luas (ha)", "Status"]
        )
        if dataFrame.empty:
            print("Tidak ada data lahan")
        else:
            print("\n--- DATA LAHAN ---")
            print(dataFrame.to_string(index=False))
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def ubah_lahan():
    """
    Mengubah data lahan.
    """
    lahan_id = input("Masukkan ID lahan yang ingin diubah: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Lahan WHERE Lahan_ID = %s;", (lahan_id,))
        row = cur.fetchone()
        if row is None:
            print("Lahan tidak ditemukan.")
            return

        print("Data saat ini:", row)
        lokasi_baru = input("Lokasi baru (kosongkan jika tidak diubah): ")
        luas_baru = input("Luas baru (kosongkan jika tidak diubah): ")

        if lokasi_baru:
            cur.execute(
                "UPDATE Lahan SET lokasi = %s WHERE Lahan_ID = %s;",
                (lokasi_baru, lahan_id)
            )
        if luas_baru:
            cur.execute(
                "UPDATE Lahan SET luas_lahan = %s WHERE Lahan_ID = %s;",
                (luas_baru, lahan_id)
            )

        conn.commit()
        print("Lahan berhasil diperbarui.")
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def hapus_lahan():
    """
    Menghapus data lahan.
    TODO: cek dulu apakah lahan masih terhubung ke Detail_panen sebelum dihapus,
    supaya tidak melanggar FK constraint.
    """
    lahan_id = input("Masukkan ID lahan yang ingin dihapus: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Lahan WHERE Lahan_ID = %s;", (lahan_id,))
        conn.commit()
        print("Lahan berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# F. FITUR PANEN
# =========================================================

def tambah_panen():
    """
    Mencatat hasil panen baru.
    Membuat 1 baris Stok (penambahan), 1 baris Panen, dan 1 atau lebih
    baris Detail_panen (relasi many-to-many ke Lahan).
    """
    jumlah_hasil_panen = input("Jumlah hasil panen (gram): ")
    produk_id = input("ID Produk: ")

    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
            VALUES ('Penambahan', %s, CURRENT_DATE, TRUE, %s)
            RETURNING Stok_ID;
            """,
            (jumlah_hasil_panen, produk_id)
        )
        stok_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO Panen (tanggal_panen, jumlah_hasil_panen, Stok_ID)
            VALUES (CURRENT_DATE, %s, %s)
            RETURNING Panen_ID;
            """,
            (jumlah_hasil_panen, stok_id)
        )
        panen_id = cur.fetchone()[0]

        jumlah_lahan = int(input("Berapa lahan yang terlibat dalam panen ini? "))
        for i in range(jumlah_lahan):
            print(f"-- Lahan ke-{i + 1} --")
            lahan_id = input("ID Lahan: ")
            luas_dipanen = input("Luas yang dipanen (hektar): ")
            cur.execute(
                """
                INSERT INTO Detail_panen (luas_dipanen, Lahan_ID, Panen_ID)
                VALUES (%s, %s, %s);
                """,
                (luas_dipanen, lahan_id, panen_id)
            )

        cur.execute(
            "UPDATE Produk SET jumlah = jumlah + %s WHERE Produk_ID = %s;",
            (jumlah_hasil_panen, produk_id)
        )

        conn.commit()
        print("Data panen berhasil dicatat.")
    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


def lihat_panen():
    """
    Menampilkan data panen beserta lahan yang terlibat.
    """
    conn, cur = connectDB()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT p.Panen_ID, p.tanggal_panen, p.jumlah_hasil_panen,
                   STRING_AGG(l.nama_lahan, ', ') AS lahan_terlibat
            FROM Panen p
            JOIN Detail_panen dp ON dp.Panen_ID = p.Panen_ID
            JOIN Lahan l ON l.Lahan_ID = dp.Lahan_ID
            GROUP BY p.Panen_ID, p.tanggal_panen, p.jumlah_hasil_panen
            ORDER BY p.tanggal_panen DESC;
            """
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal Panen", "Jumlah Hasil", "Lahan Terlibat"]
        )
        if dataFrame.empty:
            print("Tidak ada data panen")
        else:
            print("\n--- DATA PANEN ---")
            print(dataFrame.to_string(index=False))
    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# G. FITUR TRANSAKSI
# =========================================================

def lihat_transaksi():
    """
    Menampilkan seluruh riwayat transaksi penjualan menggunakan pandas DataFrame.
    Dipakai oleh menu admin dan menu kasir.
    """
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        # Menggabungkan tabel agar ID berubah menjadi nama asli (pelanggan, produk, metode)
        cur.execute(
            """
            SELECT t.Transaksi_ID, t.tanggal, pg.nama_pengguna, pr.nama_produk,
                   t.jumlah_produk, t.total_harga, t.status_pembayaran, mp.nama_metode_pembayaran
            FROM Transaksi t
            JOIN Pengguna pg ON pg.Pengguna_ID = t.Pengguna_ID
            JOIN Produk pr ON pr.Produk_ID = t.Produk_ID
            JOIN Metode_pembayaran mp ON mp.Metode_Pembayaran_ID = t.Metode_Pembayaran_ID
            WHERE t.is_active = TRUE
            ORDER BY t.tanggal DESC, t.Transaksi_ID DESC;
            """
        )
        rows = cur.fetchall()

        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Pelanggan", "Produk", "Jumlah (gram)", "Total Harga", "Status", "Metode"]
        )

        if dataFrame.empty:
            print("Tidak ada data transaksi.")
        else:
            print("\n--- DATA TRANSAKSI ---")
            print(dataFrame.to_string(index=False))

    except Exception as e:
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# H. DASHBOARD
# =========================================================

def lihat_dashboard(batas_minimum=5000):
    """
    Menampilkan ringkasan informasi usaha.
    """
    conn, cur = connectDB()
    try:
        print("\n========== DASHBOARD ==========")

        # Stok produk saat ini
        cur.execute("SELECT nama_produk, jumlah FROM Produk;")
        rows = cur.fetchall()
        df_produk = pd.DataFrame(rows, columns=["Nama Produk", "Jumlah"])
        print("\n-- Stok Produk Saat Ini --")
        print(df_produk.to_string(index=False))

        # Notifikasi stok menipis
        stok_menipis = df_produk[df_produk["Jumlah"] < batas_minimum]
        if not stok_menipis.empty:
            print(f"\n[PERINGATAN] Produk dengan stok di bawah {batas_minimum} gram:")
            print(stok_menipis.to_string(index=False))
        else:
            print("\nStok semua produk masih aman.")

        # Total transaksi & pendapatan
        cur.execute(
            """
            SELECT t.total_harga, t.status_pembayaran
            FROM Transaksi t
            """
        )
        rows = cur.fetchall()
        df_transaksi = pd.DataFrame(rows, columns=["Total Harga", "Status"])

        if df_transaksi.empty:
            print("\nTidak ada data transaksi")
        else:
            total_transaksi = len(df_transaksi)
            total_pendapatan = df_transaksi.loc[df_transaksi["Status"] == "Lunas", "Total Harga"].sum()

            print(f"\nTotal transaksi tercatat : {total_transaksi}")
            print(f"Total pendapatan (Lunas) : Rp{total_pendapatan:,.2f}")

            print("\n-- Transaksi per Status Pembayaran --")
            print(df_transaksi.groupby("Status").size().to_string())

    except Exception as e:
        print("Terjadi kesalahan", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# MENU UTAMA (CLI)
# =========================================================

def menu_akun():
    while True:
        cetak_subheader("FITUR AKUN")
        print("1. Tambah Akun")
        print("2. Lihat Akun")
        print("3. Ubah Akun")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_akun()
        elif pilihan == "2":
            lihat_akun()
        elif pilihan == "3":
            ubah_akun()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_produk():
    while True:
        cetak_subheader("FITUR PRODUK")
        print("1. Tambah Produk")
        print("2. Lihat Produk")
        print("3. Ubah Produk")
        print("4. Hapus Produk")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_produk()
        elif pilihan == "2":
            lihat_produk()
        elif pilihan == "3":
            ubah_produk()
        elif pilihan == "4":
            hapus_produk()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_stok():
    while True:
        cetak_subheader("FITUR STOK")
        print("1. Tambah Stok")
        print("2. Lihat Stok")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_stok()
        elif pilihan == "2":
            lihat_stok()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_produk_rusak():
    while True:
        cetak_subheader("FITUR PRODUK RUSAK")
        print("1. Tambah Produk Rusak")
        print("2. Lihat Produk Rusak")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_produk_rusak()
        elif pilihan == "2":
            lihat_produk_rusak()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_lahan():
    while True:
        cetak_subheader("FITUR LAHAN")
        print("1. Tambah Lahan")
        print("2. Lihat Lahan")
        print("3. Ubah Lahan")
        print("4. Hapus Lahan")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_lahan()
        elif pilihan == "2":
            lihat_lahan()
        elif pilihan == "3":
            ubah_lahan()
        elif pilihan == "4":
            hapus_lahan()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_panen():
    while True:
        cetak_subheader("FITUR PANEN")
        print("1. Tambah Panen")
        print("2. Lihat Panen")
        print("0. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_panen()
        elif pilihan == "2":
            lihat_panen()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")


def menu_admin():
    """
    Menu utama setelah admin berhasil login.
    """
    while True:
        lihat_dashboard()

        cetak_header("MENU ADMIN")
        print("1. Fitur Akun")
        print("2. Fitur Produk")
        print("3. Fitur Stok")
        print("4. Fitur Produk Rusak")
        print("5. Fitur Lahan")
        print("6. Fitur Panen")
        print("7. Lihat Transaksi")
        print("0. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            menu_akun()
        elif pilihan == "2":
            menu_produk()
        elif pilihan == "3":
            menu_stok()
        elif pilihan == "4":
            menu_produk_rusak()
        elif pilihan == "5":
            menu_lahan()
        elif pilihan == "6":
            menu_panen()
        elif pilihan == "7":
            lihat_transaksi()
        elif pilihan == "0":
            logout()
            break
        else:
            print("Pilihan tidak valid.")


# =========================================================
# C. FITUR TRANSAKSI (KASIR)
# =========================================================

def tambah_transaksi():
    # """
    # Mencatat transaksi penjualan baru oleh kasir.
    # Proses ini menjalankan 3 perubahan sekaligus dalam 1 transaksi database:
    # 1. Menambah baris baru di tabel Transaksi
    # 2. Mengurangi kolom jumlah (stok) di tabel Produk
    # 3. Mencatat riwayat pengeluaran barang di tabel Stok
    # """
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        print("\n--- TAMBAH TRANSAKSI PENJUALAN (KASIR) ---")

        # 1. MENAMPILKAN & MEMILIH PELANGGAN (Role_ID = 3 adalah 'Pengguna' / Pelanggan)
        cur.execute(
            """
            SELECT Pengguna_ID, nama_pengguna, no_telepon
            FROM Pengguna
            WHERE Role_ID = 3 AND is_active = TRUE
            ORDER BY Pengguna_ID ASC;
            """
        )
        rows_pelanggan = cur.fetchall()
        df_pelanggan = pd.DataFrame(rows_pelanggan, columns=["ID", "Nama Pelanggan", "No Telepon"])

        if df_pelanggan.empty:
            print("Belum ada data pelanggan aktif.")
            return

        print("\n-- Daftar Pelanggan --")
        print(df_pelanggan.to_string(index=False))

        # Mengambil daftar ID pelanggan yang valid untuk pengecekan input
        daftar_id_pelanggan = df_pelanggan["ID"].tolist()

        while True:
            try:
                pengguna_id = int(input("\nMasukkan ID Pelanggan (0 untuk batal): "))
                if pengguna_id == 0:
                    print("Transaksi dibatalkan.")
                    return
                if pengguna_id not in daftar_id_pelanggan:
                    print("ID Pelanggan tidak ditemukan. Pilih sesuai tabel.")
                    continue
                # Mengambil nama pelanggan dari DataFrame sesuai ID yang dipilih
                nama_pelanggan = df_pelanggan.loc[df_pelanggan["ID"] == pengguna_id, "Nama Pelanggan"].values[0]
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 2. MENAMPILKAN & MEMILIH PRODUK YANG STOKNYA TERSEDIA (> 0)
        cur.execute(
            """
            SELECT Produk_ID, nama_produk, harga, jumlah
            FROM Produk
            WHERE is_active = TRUE AND jumlah > 0
            ORDER BY Produk_ID ASC;
            """
        )
        rows_produk = cur.fetchall()
        df_produk = pd.DataFrame(rows_produk, columns=["ID", "Nama Produk", "Harga", "Stok (gram)"])

        if df_produk.empty:
            print("Semua stok produk sedang habis (0 gram).")
            return

        print("\n-- Daftar Produk Tersedia --")
        print(df_produk.to_string(index=False))

        daftar_id_produk = df_produk["ID"].tolist()

        while True:
            try:
                produk_id = int(input("\nMasukkan ID Produk yang dibeli (0 untuk batal): "))
                if produk_id == 0:
                    print("Transaksi dibatalkan.")
                    return
                if produk_id not in daftar_id_produk:
                    print("ID Produk tidak ditemukan. Pilih sesuai tabel.")
                    continue

                # Mengambil detail baris produk yang dipilih dari DataFrame
                baris_produk = df_produk.loc[df_produk["ID"] == produk_id].iloc[0]
                nama_produk = baris_produk["Nama Produk"]
                harga_satuan = baris_produk["Harga"]
                stok_tersedia = int(baris_produk["Stok (gram)"])
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 3. INPUT JUMLAH PEMBELIAN (GRAM) & VALIDASI STOK
        while True:
            try:
                qty = int(input(f"Masukkan jumlah pembelian dalam gram (Maksimal {stok_tersedia} gr): "))
                if qty <= 0:
                    print("Jumlah pembelian harus lebih dari 0.")
                    continue
                if qty > stok_tersedia:
                    print(f"Stok tidak mencukupi! Sisa stok hanya {stok_tersedia} gram.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka bulat.")

        # Menghitung total harga otomatis
        total_harga = harga_satuan * qty

        # 4. MEMILIH METODE PEMBAYARAN
        cur.execute("SELECT Metode_Pembayaran_ID, nama_metode_pembayaran FROM Metode_pembayaran ORDER BY Metode_Pembayaran_ID ASC;")
        rows_metode = cur.fetchall()
        df_metode = pd.DataFrame(rows_metode, columns=["ID", "Metode Pembayaran"])
        print("\n-- Metode Pembayaran --")
        print(df_metode.to_string(index=False))

        while True:
            try:
                metode_id = int(input("Pilih ID Metode Pembayaran: "))
                if metode_id not in df_metode["ID"].tolist():
                    print("ID Metode Pembayaran tidak valid.")
                    continue
                nama_metode = df_metode.loc[df_metode["ID"] == metode_id, "Metode Pembayaran"].values[0]
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 5. MEMILIH STATUS PEMBAYARAN (langsung dari nilai enum)
        print("\n-- Status Pembayaran --")
        for i, status in enumerate(STATUS_PEMBAYARAN, start=1):
            print(f"{i}. {status}")

        while True:
            try:
                pilihan_status = int(input("Pilih nomor Status Pembayaran: "))
                if pilihan_status < 1 or pilihan_status > len(STATUS_PEMBAYARAN):
                    print("Pilihan Status Pembayaran tidak valid.")
                    continue
                nama_status = STATUS_PEMBAYARAN[pilihan_status - 1]
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 6. RINGKASAN & KONFIRMASI AKHIR
        print("\n--- RINGKASAN TRANSAKSI ---")
        print(f"Pelanggan   : {nama_pelanggan}")
        print(f"Produk      : {nama_produk}")
        print(f"Jumlah      : {qty} gram")
        print(f"Total Harga : Rp{total_harga:,.2f}")
        print(f"Pembayaran  : {nama_metode} ({nama_status})")

        konfirmasi = input("\nSimpan transaksi ini? (y/n): ").lower()
        if konfirmasi != "y":
            print("Transaksi dibatalkan.")
            return

        # 7. EKSEKUSI QUERY KE DATABASE (Transaksi, Produk, dan Stok)
        # A. Simpan ke tabel Transaksi dan ambil Transaksi_ID yang baru terbentuk
        cur.execute(
            """
            INSERT INTO Transaksi
                (tanggal, total_harga, jumlah_produk, status_pembayaran, is_active, Produk_ID, Pengguna_ID, Metode_Pembayaran_ID)
            VALUES (CURRENT_DATE, %s, %s, %s, TRUE, %s, %s, %s)
            RETURNING Transaksi_ID, tanggal;
            """,
            (total_harga, qty, nama_status, produk_id, pengguna_id, metode_id)
        )
        transaksi_id, tgl_transaksi = cur.fetchone()

        # B. Kurangi stok pada tabel Produk
        cur.execute(
            "UPDATE Produk SET jumlah = jumlah - %s WHERE Produk_ID = %s;",
            (qty, produk_id)
        )

        # C. Catat log pengeluaran barang ke tabel Stok
        cur.execute(
            """
            INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
            VALUES ('Pengeluaran', %s, CURRENT_DATE, TRUE, %s);
            """,
            (qty, produk_id)
        )

        # Simpan seluruh perubahan secara permanen ke PostgreSQL
        conn.commit()

        # Cetak struk sederhana
        print("\n========== STRUK TRANSAKSI ==========")
        print(f"No. Transaksi : TRX-{transaksi_id:04d}")
        print(f"Tanggal       : {tgl_transaksi}")
        print(f"Pelanggan     : {nama_pelanggan}")
        print(f"Produk        : {nama_produk}")
        print(f"Jumlah        : {qty} gram")
        print(f"Total Bayar   : Rp{total_harga:,.2f}")
        print(f"Pembayaran    : {nama_metode} ({nama_status})")
        print("=====================================")
        print("Transaksi berhasil dicatat dan stok otomatis berkurang.")

    except Exception as e:
        # Batalkan semua query di atas jika terjadi error di tengah jalan agar stok tidak selisih
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


def ubah_status_pembayaran():
    """
    Mengubah status pembayaran transaksi pelanggan (misalnya dari 'Menunggu konfirmasi' menjadi 'Lunas').
    """
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        # Mengambil transaksi aktif yang status pembayarannya BELUM 'Lunas'
        cur.execute(
            """
            SELECT t.Transaksi_ID, t.tanggal, pg.nama_pengguna, pr.nama_produk,
                   t.jumlah_produk, t.total_harga, mp.nama_metode_pembayaran, t.status_pembayaran
            FROM Transaksi t
            JOIN Pengguna pg ON pg.Pengguna_ID = t.Pengguna_ID
            JOIN Produk pr ON pr.Produk_ID = t.Produk_ID
            JOIN Metode_pembayaran mp ON mp.Metode_Pembayaran_ID = t.Metode_Pembayaran_ID
            WHERE t.is_active = TRUE AND t.status_pembayaran != 'Lunas'
            ORDER BY t.Transaksi_ID ASC;
            """
        )
        rows = cur.fetchall()

        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Pelanggan", "Produk", "Jumlah (gram)", "Total Harga", "Metode", "Status"]
        )

        if dataFrame.empty:
            print("\nSemua transaksi sudah berstatus Lunas. Tidak ada yang perlu dikonfirmasi.")
            return

        print("\n--- DAFTAR TRANSAKSI BELUM LUNAS ---")
        print(dataFrame.to_string(index=False))

        daftar_id_valid = dataFrame["ID"].tolist()

        while True:
            try:
                transaksi_id = int(input("\nMasukkan ID Transaksi yang ingin diubah statusnya (0 untuk batal): "))
                if transaksi_id == 0:
                    print("Perubahan status dibatalkan.")
                    return
                if transaksi_id not in daftar_id_valid:
                    print("ID Transaksi tidak ada di dalam daftar di atas.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka.")

        # Menampilkan daftar status pembayaran (nilai enum)
        print("\n-- Pilih Status Pembayaran Baru --")
        for i, status in enumerate(STATUS_PEMBAYARAN, start=1):
            print(f"{i}. {status}")

        while True:
            try:
                pilihan_status_baru = int(input("Masukkan nomor Status baru: "))
                if pilihan_status_baru < 1 or pilihan_status_baru > len(STATUS_PEMBAYARAN):
                    print("Pilihan Status tidak valid.")
                    continue
                nama_status_baru = STATUS_PEMBAYARAN[pilihan_status_baru - 1]
                break
            except ValueError:
                print("Input harus berupa angka.")

        konfirmasi = input(f"Yakin ubah status Transaksi ID {transaksi_id} menjadi '{nama_status_baru}'? (y/n): ").lower()
        if konfirmasi != "y":
            print("Perubahan status dibatalkan.")
            return

        # Memperbarui status pembayaran di tabel Transaksi
        cur.execute(
            "UPDATE Transaksi SET status_pembayaran = %s WHERE Transaksi_ID = %s;",
            (nama_status_baru, transaksi_id)
        )
        conn.commit()
        print(f"Status Transaksi ID {transaksi_id} berhasil diperbarui menjadi '{nama_status_baru}'.")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# PEMBATALAN PESANAN
# =========================================================

def _proses_pembatalan(cur, transaksi_id):
    """
    Inti pembatalan pesanan (atomik, tanpa commit).
    Melakukan 3 perubahan sekaligus:
    1. Mengubah status pembayaran menjadi 'Dibatalkan'
    2. Mengembalikan jumlah stok pada tabel Produk
    3. Mencatat penambahan stok pada tabel Stok
    Mengembalikan (True, "") bila berhasil, atau (False, pesan) bila gagal.
    """
    cur.execute(
        """
        SELECT Produk_ID, jumlah_produk, status_pembayaran
        FROM Transaksi
        WHERE Transaksi_ID = %s AND is_active = TRUE
        FOR UPDATE;
        """,
        (transaksi_id,)
    )
    row = cur.fetchone()
    if row is None:
        return False, "Transaksi tidak ditemukan."

    produk_id, jumlah_produk, status = row
    if status in ("Lunas", "Dibatalkan"):
        return False, f"Transaksi berstatus '{status}' tidak dapat dibatalkan."

    cur.execute(
        "UPDATE Transaksi SET status_pembayaran = 'Dibatalkan' WHERE Transaksi_ID = %s;",
        (transaksi_id,)
    )
    cur.execute(
        "UPDATE Produk SET jumlah = jumlah + %s WHERE Produk_ID = %s;",
        (jumlah_produk, produk_id)
    )
    cur.execute(
        """
        INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
        VALUES ('Penambahan', %s, CURRENT_DATE, TRUE, %s);
        """,
        (jumlah_produk, produk_id)
    )
    return True, ""


def batalkan_pesanan_kasir():
    """
    Membatalkan pesanan pelanggan mana pun yang belum lunas/dibatalkan.
    Stok pesanan dikembalikan dan dicatat sebagai 'Penambahan'.
    """
    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT t.Transaksi_ID, t.tanggal, pg.nama_pengguna, pr.nama_produk,
                   t.jumlah_produk, t.total_harga, t.status_pembayaran, mp.nama_metode_pembayaran
            FROM Transaksi t
            JOIN Pengguna pg ON pg.Pengguna_ID = t.Pengguna_ID
            JOIN Produk pr ON pr.Produk_ID = t.Produk_ID
            JOIN Metode_pembayaran mp ON mp.Metode_Pembayaran_ID = t.Metode_Pembayaran_ID
            WHERE t.is_active = TRUE
              AND t.status_pembayaran NOT IN ('Lunas', 'Dibatalkan')
            ORDER BY t.tanggal DESC, t.Transaksi_ID DESC;
            """
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Pelanggan", "Produk", "Jumlah (gram)", "Total Harga", "Status", "Metode"]
        )

        if dataFrame.empty:
            print("\nTidak ada pesanan yang bisa dibatalkan.")
            return

        print("\n--- BATALKAN PESANAN PELANGGAN ---")
        print(dataFrame.to_string(index=False))

        daftar_id_valid = dataFrame["ID"].tolist()

        while True:
            try:
                transaksi_id = int(input("\nMasukkan ID Pesanan yang ingin dibatalkan (0 untuk batal): "))
                if transaksi_id == 0:
                    print("Pembatalan pesanan dibatalkan.")
                    return
                if transaksi_id not in daftar_id_valid:
                    print("ID Pesanan tidak ada di dalam daftar di atas.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka.")

        konfirmasi = input(f"Yakin batalkan Pesanan ID {transaksi_id}? (y/n): ").lower()
        if konfirmasi != "y":
            print("Pembatalan pesanan dibatalkan.")
            return

        berhasil, pesan = _proses_pembatalan(cur, transaksi_id)
        if berhasil:
            conn.commit()
            print(f"Pesanan ID {transaksi_id} berhasil dibatalkan dan stok telah dikembalikan.")
        else:
            conn.rollback()
            print(f"Pembatalan gagal: {pesan}")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# MENU UTAMA (CLI)
# =========================================================

def menu_karyawan():
    """
    Menu utama setelah karyawan berhasil login.
    """
    while True:
        cetak_header("MENU KARYAWAN (KASIR)")
        print("1. Lihat Data Produk")
        print("2. Tambah Transaksi Penjualan")
        print("3. Ubah Status Pembayaran")
        print("4. Lihat Riwayat Transaksi")
        print("5. Batalkan Pesanan Pelanggan")
        print("0. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            lihat_produk()
        elif pilihan == "2":
            tambah_transaksi()
        elif pilihan == "3":
            ubah_status_pembayaran()
        elif pilihan == "4":
            lihat_transaksi()
        elif pilihan == "5":
            batalkan_pesanan_kasir()
        elif pilihan == "0":
            logout()
            break
        else:
            print("Pilihan tidak valid.")

def ubah_profil(akun):
    """
    Mengubah data profil pelanggan yang sedang login (nama, no telepon, username, atau password).
    Parameter 'akun' adalah dictionary berisi {'id': ..., 'nama': ..., 'role': ...}.
    """
    pengguna_id = akun["id"]

    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        # Mengambil data profil saat ini berdasarkan Pengguna_ID
        cur.execute(
            """
            SELECT Pengguna_ID, nama_pengguna, email, no_telepon, username
            FROM Pengguna
            WHERE Pengguna_ID = %s;
            """,
            (pengguna_id,)
        )
        row = cur.fetchone()
        if row is None:
            print("Data akun tidak ditemukan.")
            return

        # Menampilkan profil saat ini menggunakan pandas DataFrame
        df_profil = pd.DataFrame(
            [row],
            columns=["ID", "Nama", "Email", "No Telepon", "Username"]
        )
        print("\n--- PROFIL SAYA SAAT INI ---")
        print(df_profil.to_string(index=False))

        print("\n(Kosongkan dan langsung tekan Enter jika bagian tersebut tidak ingin diubah)")
        nama_baru = input("Nama baru       : ").strip()
        telp_baru = input("No. telepon baru: ").strip()
        user_baru = input("Username baru   : ").strip()
        pass_baru = input("Password baru   : ").strip()

        # Memperbarui kolom satu per satu jika diisi oleh pengguna
        if nama_baru:
            cur.execute(
                "UPDATE Pengguna SET nama_pengguna = %s WHERE Pengguna_ID = %s;",
                (nama_baru, pengguna_id)
            )
            akun["nama"] = nama_baru  # Perbarui nama di variabel sesi aktif

        if telp_baru:
            if not telp_baru.isdigit() or len(telp_baru) > 13:
                print("No. telepon tidak valid (harus angka maksimal 13 digit). Perubahan dibatalkan.")
                conn.rollback()
                return
            cur.execute(
                "UPDATE Pengguna SET no_telepon = %s WHERE Pengguna_ID = %s;",
                (telp_baru, pengguna_id)
            )

        if user_baru:
            cur.execute(
                "UPDATE Pengguna SET username = %s WHERE Pengguna_ID = %s;",
                (user_baru, pengguna_id)
            )

        if pass_baru:
            cur.execute(
                "UPDATE Pengguna SET password_ = %s WHERE Pengguna_ID = %s;",
                (pass_baru, pengguna_id)
            )

        conn.commit()
        print("Profil akun berhasil diperbarui.")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# C. FITUR PESANAN
# =========================================================

def tambah_pesanan(akun):
    """
    Membuat pesanan baru oleh pelanggan.
    Menjalankan 3 perintah database sekaligus dalam 1 transaksi:
    1. Mencatat pesanan ke tabel Transaksi
    2. Mengurangi stok pada tabel Produk
    3. Mencatat riwayat pengeluaran barang ke tabel Stok
    """
    pengguna_id = akun["id"]
    nama_pelanggan = akun["nama"]

    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        print("\n--- BUAT PESANAN BARU ---")

        # 1. MENAMPILKAN PRODUK YANG STOKNYA TERSEDIA (> 0)
        cur.execute(
            """
            SELECT Produk_ID, nama_produk, harga, jumlah
            FROM Produk
            WHERE is_active = TRUE AND jumlah > 0
            ORDER BY Produk_ID ASC;
            """
        )
        rows_produk = cur.fetchall()
        df_produk = pd.DataFrame(rows_produk, columns=["ID", "Nama Produk", "Harga/Gram", "Stok (gram)"])

        if df_produk.empty:
            print("Mohon maaf, semua stok produk sedang habis (0 gram).")
            return

        print("\n-- Daftar Produk Tersedia --")
        print(df_produk.to_string(index=False))

        daftar_id_produk = df_produk["ID"].tolist()

        # 2. MEMILIH ID PRODUK
        while True:
            try:
                produk_id = int(input("\nMasukkan ID Produk yang ingin dipesan (0 untuk batal): "))
                if produk_id == 0:
                    print("Pemesanan dibatalkan.")
                    return
                if produk_id not in daftar_id_produk:
                    print("ID Produk tidak ditemukan. Pilih sesuai tabel.")
                    continue

                # Mengambil detail baris produk yang dipilih dari DataFrame
                baris_produk = df_produk.loc[df_produk["ID"] == produk_id].iloc[0]
                nama_produk = baris_produk["Nama Produk"]
                harga_satuan = baris_produk["Harga/Gram"]
                stok_tersedia = int(baris_produk["Stok (gram)"])
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 3. INPUT JUMLAH PESANAN (GRAM) & VALIDASI STOK
        while True:
            try:
                qty = int(input(f"Masukkan jumlah pesanan dalam gram (Maksimal {stok_tersedia} gr): "))
                if qty <= 0:
                    print("Jumlah pesanan harus lebih dari 0.")
                    continue
                if qty > stok_tersedia:
                    print(f"Stok tidak mencukupi! Sisa stok hanya {stok_tersedia} gram.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka bulat.")

        # Menghitung total tagihan otomatis
        total_harga = harga_satuan * qty

        # 4. MEMILIH METODE PEMBAYARAN (Cash / Transfer)
        cur.execute("SELECT Metode_Pembayaran_ID, nama_metode_pembayaran FROM Metode_pembayaran ORDER BY Metode_Pembayaran_ID ASC;")
        rows_metode = cur.fetchall()
        df_metode = pd.DataFrame(rows_metode, columns=["ID", "Metode Pembayaran"])

        print("\n-- Pilih Metode Pembayaran --")
        print(df_metode.to_string(index=False))

        while True:
            try:
                metode_id = int(input("Masukkan ID Metode Pembayaran: "))
                if metode_id not in df_metode["ID"].tolist():
                    print("ID Metode Pembayaran tidak valid.")
                    continue
                nama_metode = df_metode.loc[df_metode["ID"] == metode_id, "Metode Pembayaran"].values[0]
                break
            except ValueError:
                print("Input harus berupa angka.")

        # 5. MENENTUKAN STATUS AWAL PEMBAYARAN SECARA OTOMATIS
        # Jika Cash -> 'Belum dibayar' (dibayar saat ambil barang di toko)
        # Jika Transfer -> 'Menunggu konfirmasi' (dicek oleh kasir)
        nama_status = "Belum dibayar" if nama_metode == "Cash" else "Menunggu konfirmasi"

        # 6. RINGKASAN & KONFIRMASI PESANAN
        print("\n--- RINGKASAN PESANAN ---")
        print(f"Pemesan     : {nama_pelanggan}")
        print(f"Produk      : {nama_produk}")
        print(f"Jumlah      : {qty} gram")
        print(f"Total Harga : Rp{total_harga:,.2f}")
        print(f"Metode      : {nama_metode}")
        print(f"Status Awal : {nama_status}")

        konfirmasi = input("\nKirim pesanan ini sekarang? (y/n): ").lower()
        if konfirmasi != "y":
            print("Pemesanan dibatalkan.")
            return

        # 7. MENYIMPAN PESANAN KE DATABASE (Transaksi, Produk, dan Stok)
        cur.execute(
            """
            INSERT INTO Transaksi
                (tanggal, total_harga, jumlah_produk, status_pembayaran, is_active, Produk_ID, Pengguna_ID, Metode_Pembayaran_ID)
            VALUES (CURRENT_DATE, %s, %s, %s, TRUE, %s, %s, %s)
            RETURNING Transaksi_ID, tanggal;
            """,
            (total_harga, qty, nama_status, produk_id, pengguna_id, metode_id)
        )
        transaksi_id, tgl_pesan = cur.fetchone()

        # Mengurangi jumlah stok produk
        cur.execute(
            "UPDATE Produk SET jumlah = jumlah - %s WHERE Produk_ID = %s;",
            (qty, produk_id)
        )

        # Mencatat pengeluaran stok di tabel Stok
        cur.execute(
            """
            INSERT INTO Stok (tipe, jumlah_stok, tanggal_pembaruan, is_active, Produk_ID)
            VALUES ('Pengeluaran', %s, CURRENT_DATE, TRUE, %s);
            """,
            (qty, produk_id)
        )

        conn.commit()

        # Mencetak bukti pemesanan
        print("\n========== BUKTI PEMESANAN ==========")
        print(f"Kode Pesanan  : TRX-{transaksi_id:04d}")
        print(f"Tanggal       : {tgl_pesan}")
        print(f"Produk        : {nama_produk} ({qty} gram)")
        print(f"Total Tagihan : Rp{total_harga:,.2f}")
        print(f"Metode Bayar  : {nama_metode}")
        print(f"Status        : {nama_status}")
        print("=====================================")
        print("Pesanan berhasil dibuat! Tunjukkan kode pesanan ke kasir saat pembayaran.")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


def lihat_pembelian(akun):
    """
    Menampilkan riwayat pembelian khusus milik pelanggan yang sedang login.
    """
    pengguna_id = akun["id"]

    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        # WHERE t.Pengguna_ID = %s memastikan pelanggan hanya melihat transaksinya sendiri
        cur.execute(
            """
            SELECT t.Transaksi_ID, t.tanggal, pr.nama_produk, t.jumlah_produk,
                   t.total_harga, t.status_pembayaran, mp.nama_metode_pembayaran
            FROM Transaksi t
            JOIN Produk pr ON pr.Produk_ID = t.Produk_ID
            JOIN Metode_pembayaran mp ON mp.Metode_Pembayaran_ID = t.Metode_Pembayaran_ID
            WHERE t.Pengguna_ID = %s AND t.is_active = TRUE
            ORDER BY t.tanggal DESC, t.Transaksi_ID DESC;
            """,
            (pengguna_id,)
        )
        rows = cur.fetchall()

        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Produk", "Jumlah (gram)", "Total Harga", "Status", "Metode"]
        )

        if dataFrame.empty:
            print("\nAnda belum memiliki riwayat pembelian.")
        else:
            print("\n--- RIWAYAT PEMBELIAN SAYA ---")
            print(dataFrame.to_string(index=False))

    except Exception as e:
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


def batalkan_pesanan_saya(akun):
    """
    Membatalkan pesanan milik pelanggan yang sedang login.
    Stok pesanan dikembalikan dan dicatat sebagai 'Penambahan'.
    """
    pengguna_id = akun["id"]

    conn = get_connection()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        # WHERE t.Pengguna_ID = %s memastikan pelanggan hanya bisa membatalkan pesanannya sendiri
        cur.execute(
            """
            SELECT t.Transaksi_ID, t.tanggal, pr.nama_produk, t.jumlah_produk,
                   t.total_harga, t.status_pembayaran, mp.nama_metode_pembayaran
            FROM Transaksi t
            JOIN Produk pr ON pr.Produk_ID = t.Produk_ID
            JOIN Metode_pembayaran mp ON mp.Metode_Pembayaran_ID = t.Metode_Pembayaran_ID
            WHERE t.Pengguna_ID = %s AND t.is_active = TRUE
              AND t.status_pembayaran NOT IN ('Lunas', 'Dibatalkan')
            ORDER BY t.tanggal DESC, t.Transaksi_ID DESC;
            """,
            (pengguna_id,)
        )
        rows = cur.fetchall()
        dataFrame = pd.DataFrame(
            rows,
            columns=["ID", "Tanggal", "Produk", "Jumlah (gram)", "Total Harga", "Status", "Metode"]
        )

        if dataFrame.empty:
            print("\nTidak ada pesanan yang bisa dibatalkan.")
            return

        print("\n--- BATALKAN PESANAN SAYA ---")
        print(dataFrame.to_string(index=False))

        daftar_id_valid = dataFrame["ID"].tolist()

        while True:
            try:
                transaksi_id = int(input("\nMasukkan ID Pesanan yang ingin dibatalkan (0 untuk batal): "))
                if transaksi_id == 0:
                    print("Pembatalan pesanan dibatalkan.")
                    return
                if transaksi_id not in daftar_id_valid:
                    print("ID Pesanan tidak ada di dalam daftar di atas.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka.")

        konfirmasi = input(f"Yakin batalkan Pesanan ID {transaksi_id}? (y/n): ").lower()
        if konfirmasi != "y":
            print("Pembatalan pesanan dibatalkan.")
            return

        berhasil, pesan = _proses_pembatalan(cur, transaksi_id)
        if berhasil:
            conn.commit()
            print(f"Pesanan ID {transaksi_id} berhasil dibatalkan dan stok telah dikembalikan.")
        else:
            conn.rollback()
            print(f"Pembatalan gagal: {pesan}")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()


# =========================================================
# MENU UTAMA (CLI)
# =========================================================

def menu_pelanggan(akun):
    """
    Menu utama setelah pelanggan berhasil login.
    """
    while True:
        cetak_header(f"MENU PELANGGAN - {akun['nama']}")
        print("1. Lihat Katalog Produk")
        print("2. Buat Pesanan Baru")
        print("3. Lihat Riwayat Pembelian Saya")
        print("4. Ubah Profil Akun")
        print("0. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == '1':
            lihat_produk()
        elif pilihan == '2':
            tambah_pesanan(akun)
        elif pilihan == '3':   
            lihat_pembelian(akun)
        elif pilihan == '4':
            ubah_profil(akun)
        elif pilihan == '0':
            logout()
            break
        else:
            print("Pilihan tidak valid.")



if __name__ == "__main__":
    conn, cur = connectDB()

    if conn is not None:
        print("Berhasil terhubung ke PostgreSQL!")

        while True:
            cetak_header("SIPETRA - SISTEM PEMESANAN TEMBAKAU")
            print("1. Login")
            print("2. Register")
            print("0. Keluar")
            pilihan_awal = input("Pilih menu: ")

            if pilihan_awal == "1":
                data_user = login()
                break
            elif pilihan_awal == "2":
                register()
                continue
            elif pilihan_awal == "0":
                print("Terima kasih. Sampai jumpa!")
                data_user = None
                break
            else:
                print("Pilihan tidak valid.")
                continue

        if data_user is not None:

            if data_user["role"] == "Admin":
                menu_admin()

            elif data_user["role"] == "Karyawan":
                menu_karyawan()

            elif data_user["role"] == "Pengguna":
                menu_pelanggan(data_user)

            else:
                print("Role tidak dikenali:", data_user["role"])

        else:
            print("Login gagal. Silakan coba kembali.")

        cur.close()
        conn.close()

    else:
        print("Gagal terhubung ke database.")


