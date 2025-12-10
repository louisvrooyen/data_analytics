import mysql.connector
import config
import tkinter as tk
from tkinter import ttk

def get_connection():
    return mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME,
        autocommit=True
    )

def fetch_street_data(limit=200, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    sql = f"""
    SELECT 
        sf.ID AS Street_ID,
        sf.Main_Road AS Main_Road,
        sf.Suburb AS Suburb,
        sf.Town AS Town,
        sf.Town AS City,
        sf.X_Road AS X_Road,
        sf.Latitude AS XRoad_Latitude,
        sf.Longitude AS XRoad_Longitude,
        r.Region_ID AS Region_ID,
        r.Region_Name AS Region_Name,
        stf.Fire_Station AS Fire_Station
    FROM
        (((incidents.streets_lookup_full sf
        JOIN incidents.region_suburbs rs ON (sf.Suburb = rs.suburb))
        JOIN incidents.suburb_to_firestation stf ON (stf.Suburb = rs.suburb))
        JOIN incidents.regions r ON (rs.region = r.Region_Name))
    ORDER BY sf.ID, sf.Main_Road, sf.Suburb, stf.Fire_Station, r.Region_Name
    LIMIT {limit} OFFSET {offset};
    """

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    conn.close()
    return columns, rows

class StreetDataGrid:
    def __init__(self, root, page_size=200):
        self.root = root
        self.page_size = page_size
        self.offset = 0

        self.columns, self.rows = fetch_street_data(self.page_size, self.offset)

        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        vsb = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Paging + Refresh controls
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.prev_btn = tk.Button(btn_frame, text="Previous", command=self.prev_page)
        self.next_btn = tk.Button(btn_frame, text="Next", command=self.next_page)
        self.refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.refresh_page)

        self.prev_btn.pack(side="left", padx=5)
        self.next_btn.pack(side="left", padx=5)
        self.refresh_btn.pack(side="left", padx=5)

        # Status label (ASCII only)
        self.status_label = tk.Label(root, text="", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.load_data()

    def load_data(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch new page
        self.columns, self.rows = fetch_street_data(self.page_size, self.offset)
        for row in self.rows:
            self.tree.insert("", "end", values=row)

        # Update status label (safe ASCII string)
        page_num = (self.offset // self.page_size) + 1
        start_row = self.offset + 1
        end_row = self.offset + len(self.rows)
        self.status_label.config(text=f"Page {page_num} - Showing rows {start_row} to {end_row}")

    def next_page(self):
        self.offset += self.page_size
        self.load_data()

    def prev_page(self):
        if self.offset >= self.page_size:
            self.offset -= self.page_size
        self.load_data()

    def refresh_page(self):
        self.load_data()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Street Lookup Data (Paged)")
    # Full screen
    root.state("zoomed")   # Windows
    # root.attributes("-fullscreen", True)  # Alternative for Linux/macOS
    app = StreetDataGrid(root, page_size=config.BATCH_SIZE)
    root.mainloop()