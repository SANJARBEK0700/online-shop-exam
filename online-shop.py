from reportlab.pdfgen import canvas
import qrcode
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


class User:
    def __init__(self, name, balance, username, password):
        self.name = name
        self.balance = balance
        self.username = username
        self.password = password
        self.basket = []
        self.purchased = []
    def user_balance(self):
        print(self.balance)

class Shop:
    def __init__(self, name):
        self.name = name
        self.admin_username = "admin"
        self.admin_password = 8086
        self.balance = 0
        self.products = []
        self.users = []

    # ---------------- ADMIN ----------------

    def add_product(self):
        name = input("Enter product name: ")
        quantity = int(input("Enter product quantity: "))
        price = int(input("Enter price: "))
        for i in self.products:
            if name == self.products[i].name:
                print("Product already exists")
            else:
                self.products.append(Product(name, price, quantity))
                print("Product added.\n")
    def view_products(self):
        if not self.products:
            print("No products.")
            return
        print("\n=== PRODUCTS ===")
        for i, p in enumerate(self.products, 1):
            print(f"{i}. {p.name} - Price: {p.price}, Quantity: {p.quantity}")
        print()

    def delete_product(self):
        self.view_products()
        index = int(input("Index to delete: "))
        if 1 <= index <= len(self.products):
            self.products.pop(index - 1)
            print("Deleted.\n")

    def edit_product(self):
        self.view_products()
        index = int(input("Index to edit: "))
        if 1 <= index <= len(self.products):
            name = input("New name: ")
            quantity = int(input("New quantity: "))
            price = int(input("New price: "))
            self.products[index - 1] = Product(name, price, quantity)
            print("Edited.\n")

    # ---------------- USER ----------------

    def register_user(self):
        name = input("Enter name: ")
        balance = int(input("Enter balance: "))
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.users.append(User(name, balance, username, password))
        print("User registered!\n")

    def view_users(self):
        if not self.users:
            print("No users.\n")
        else:
            for u in self.users:
                print(f"{u.username} - Price: {u.price}, Quantity: {u.quantity}")

    def login(self):
        username = input("Username: ")
        password = input("Password: ")

        for u in self.users:
            if u.username == username and u.password == password:
                print("Login successful!\n")
                return u

        print("Wrong login!\n")
        return None

    # ---------------- SHOPPING ----------------

    def shopping(self, user):
        self.view_products()
        if 1 <= len(self.products):
            index = int(input("Enter product index: "))
            quantity = int(input("How many do you want?: "))
            if 1 <= index:
                product = self.products[index - 1]

                if quantity > product.quantity:
                    print("Not enough quantity.\n")
                    return

                total_price = quantity * product.price

                if user.balance < total_price:
                    print("Not enough balance!\n")
                    return

            # Remove from shop
                product.quantity -= quantity

            # Add to basket
                user.basket.append(Product(product.name, product.price, quantity))

            # If quantity becomes 0, remove
                if product.quantity == 0:
                    self.products.pop(index - 1)

                print("Added to basket!\n")

    # Admin balance
    def admin_balance(self):
        print(f"Shop balance {self.balance}")

    def view_basket(self, user):
        if not user.basket:
            print("Basket empty.\n")
            return

        print("\n=== YOUR BASKET ===")
        total = 0
        for i, p in enumerate(user.basket, 1):
            print(f"{i}. {p.name} x{p.quantity} - {p.price} each")
            total += p.quantity * p.price
        print(f"Total price: {total}\n")

        choice = input("Buy? (y/n/e): ")
        if choice.lower() == 'y':
            if user.balance >= total:
                user.balance -= total
                self.balance += total
                user.purchased.extend(user.basket)
                self.generate_pdf(user)
                user.basket.clear()
                print("Purchased successfully!\n")
            else:
                print("Not enough money!\n")
        elif choice.lower() == 'e':
            index = int(input("Enter index: "))
            quantity1 = int(input("Enter new quantity: "))
            if user.balance < total:
                user.basket[index-1].quantity = quantity1

    def archive(self, user):
        print("\n=== YOUR BASKET ARCHIVE ===")
        total = 0
        count = 0
        for i in user.purchased:
            total += i.quantity * i.price
            count += 1
            print(f"{count}. {i.name} - {i.price} each")
            print(f'Overall: {total}\n')

    def generate_pdf(self, user, filename=None):
        """
        Generate a PDF check for `user` using user's purchased items (or basket if purchased empty).
        Saves a QR image (temporary) and embeds it in the PDF.
        """
        # 1) tayyor filename (default: check_TIMESTAMP.pdf)
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"check_{user.username}_{ts}.pdf"

        # 2) Which items to include: purchased if exists, otherwise basket
        items = user.purchased if user.purchased else user.basket
        if not items:
            print("No items to generate receipt for.")
            return

        # 3) Prepare text lines and total
        lines = []
        total = 0.0
        for i, p in enumerate(items, 1):
            line = f"{i}. {p.name} x{p.quantity} @ {p.price} = {p.quantity * p.price:.2f}"
            lines.append(line)
            total += p.quantity * p.price

        # 4) Create QR data (simple text or JSON-like)
        qr_data = f"Shop:{self.name};User:{user.username};Total:{total:.2f};Items:{len(items)}"
        # You can expand qr_data to include lines joined, or a URL to the order.
        qr_img = qrcode.make(qr_data)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        qr_path = f"order_qr_{user.username}_{ts}.png"
        qr_img.save(qr_path)

        # 5) Create PDF and write content
        try:
            c = canvas.Canvas(filename)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 800, "ONLINE SHOP — PURCHASE CHECK")

            c.setFont("Helvetica", 10)
            c.drawString(50, 785, f"User: {user.username}")
            c.drawString(50, 770, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            y = 740
            line_height = 14
            for line in lines:
                if y < 100:  # new page if running out of space
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = 800
                c.drawString(50, y, line)
                y -= line_height

            # Leave space then write total
            if y < 120:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 800
            c.drawString(50, y - 10, f"TOTAL: {total:.2f} EUR")

            # 6) Draw QR image on the PDF using ImageReader
            try:
                img_reader = ImageReader(qr_path)
                # position QR at right side of page (adjust coords if needed)
                c.drawImage(img_reader, 400, 650, width=150, height=150)
            except Exception as e:
                print("Warning: could not draw QR image on PDF:", e)

            # 7) Save PDF
            c.save()

            # 8) Optionally remove temporary QR file
            try:
                os.remove(qr_path)
            except Exception:
                pass

            print(f"PDF saved to: {filename}")

        except Exception as e:
            print("Error generating PDF:", e)
            # clean up qr file if exists
            if os.path.exists(qr_path):
                try:
                    os.remove(qr_path)
                except Exception:
                    pass


shop = Shop("ORIGIN")
user = User("ORIGIN", 1000, "ORIGIN", "3242")

# ================= MAIN MENU =================

def shop_manager():
    while True:
        cmd = int(input("1. Admin Panel\n2. User Panel\n3. Exit\n>>> "))

        # ADMIN
        if cmd == 1:
            username = input("Admin username: ")
            password = int(input("Admin password: "))

            if username == shop.admin_username and password == shop.admin_password:
                while True:
                    print("\n=== ADMIN MENU ===")
                    cmd = int(input("1. Add Product\n2. Delete Product\n"
                                    "3. Edit Product\n4. View Products\n"
                                    "5. View Balance\n6. View Users' Info\n"
                                    "7. Exit\n>>> "))
                    if cmd == 1:
                        shop.add_product()
                    elif cmd == 2:
                        shop.delete_product()
                    elif cmd == 3:
                        shop.edit_product()
                    elif cmd == 4:
                        shop.view_products()
                    elif cmd == 5:
                        shop.admin_balance()
                    elif cmd == 6:
                        shop.view_users()
                    elif cmd == 7:
                        break
                    else:
                        print("Invalid command!\n")
            else:
                print("Wrong admin credentials!\n")

        # USER
        elif cmd == 2:
            print("\n=== USER MENU ===")
            cmd = int(input("1. Login\n2. Register\n3. Exit\n>>> "))
            if cmd == 1:
                user = shop.login()
                if user:
                    while True:
                        cmd = int(input("\n1. View Products\n2. Shopping\n3. View Basket\n4. View Balance\n5. Your Purchase History\n6. Exit\n>>> "))
                        if cmd == 1:
                            shop.view_products()
                        elif cmd == 2:
                            shop.shopping(user)
                        elif cmd == 3:
                            shop.view_basket(user)
                        elif cmd == 4:
                            user.user_balance()
                        elif cmd == 5:
                            shop.archive(user)
                        elif cmd == 6:
                            break
                        else:
                            print("Invalid command!\n")

            elif cmd == 2:
                shop.register_user()

        elif cmd == 3:
            break


shop_manager()
