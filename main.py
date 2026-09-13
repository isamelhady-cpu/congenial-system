import random
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


# تهيئة قاعدة البيانات
def init_db():
  conn = sqlite3.connect('p2p_escrow.db')
  cursor = conn.cursor()
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            booking_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
  conn.commit()
  conn.close()


init_db()


# شاشة الزبون: طلب المنتج وحجز المبلغ
class CustomerScreen(Screen):

  def __init__(self, **kwargs):
    super(CustomerScreen, self).__init__(**kwargs)
    layout = BoxLayout(orientation='vertical', padding=25, spacing=12)

    layout.add_widget(
        Label(
            text='Marketplace - Order & Escrow',
            font_size=18,
            size_hint_y=None,
            height=40,
        )
    )

    self.name_input = TextInput(
        hint_text='Customer Name', multiline=False, size_hint_y=None, height=45
    )
    layout.add_widget(self.name_input)

    self.phone_input = TextInput(
        hint_text='Phone Number', multiline=False, size_hint_y=None, height=45
    )
    layout.add_widget(self.phone_input)

    self.product_input = TextInput(
        hint_text='Product Name (e.g. Smart Watch)',
        multiline=False,
        size_hint_y=None,
        height=45,
    )
    layout.add_widget(self.product_input)

    self.amount_input = TextInput(
        hint_text='Product Amount (LYD)',
        multiline=False,
        size_hint_y=None,
        height=45,
    )
    layout.add_widget(self.amount_input)

    order_btn = Button(
        text='Request Product & Freeze Amount',
        size_hint_y=None,
        height=50,
        background_color=(0.1, 0.5, 0.8, 1),
    )
    order_btn.bind(on_press=self.create_order)
    layout.add_widget(order_btn)

    # زر الانتقال لشاشة تأكيد الاستلام للإفراج عن المبلغ
    to_release_btn = Button(
        text='Received Order? Release Funds',
        size_hint_y=None,
        height=50,
        background_color=(0.2, 0.7, 0.3, 1),
    )
    to_release_btn.bind(
        on_press=lambda x: setattr(self.manager, 'current', 'release_screen')
    )
    layout.add_widget(to_release_btn)

    # زر الانتقال للوحة تحكم التاجر
    to_admin_btn = Button(
        text='Merchant Dashboard (Admin)',
        size_hint_y=None,
        height=50,
        background_color=(0.8, 0.5, 0.1, 1),
    )
    to_admin_btn.bind(
        on_press=lambda x: setattr(self.manager, 'current', 'admin_screen')
    )
    layout.add_widget(to_admin_btn)

    self.msg_label = Label(
        text='Fill details to hold amount securely',
        font_size=13,
        size_hint_y=None,
        height=30,
    )
    layout.add_widget(self.msg_label)

    self.add_widget(layout)

  def create_order(self, instance):
    name = self.name_input.text
    phone = self.phone_input.text
    product = self.product_input.text
    amount_str = self.amount_input.text

    if not name or not phone or not product or not amount_str:
      self.msg_label.text = '⚠️ Please fill all fields!'
      return

    try:
      amount = float(amount_str)
    except ValueError:
      self.msg_label.text = '⚠️ Amount must be a number!'
      return

    booking_id = random.randint(100000, 999999)
    status = 'Amount_Held'

    conn = sqlite3.connect('p2p_escrow.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (booking_id, customer_name, phone, product, amount,'
        ' status) VALUES (?, ?, ?, ?, ?, ?)',
        (booking_id, name, phone, product, amount, status),
    )
    conn.commit()
    conn.close()

    self.name_input.text = ''
    self.phone_input.text = ''
    self.product_input.text = ''
    self.amount_input.text = ''
    self.msg_label.text = (
        f'Success! Held ID: {booking_id}\n(Funds safe until delivery)'
    )


# شاشة الزبون للإفراج عن المبلغ برقم الحجز
class ReleaseScreen(Screen):

  def __init__(self, **kwargs):
    super(ReleaseScreen, self).__init__(**kwargs)
    layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

    layout.add_widget(
        Label(
            text='Confirm Delivery & Release Funds',
            font_size=18,
            size_hint_y=None,
            height=40,
        )
    )

    self.id_input = TextInput(
        hint_text='Enter Booking ID to Release',
        multiline=False,
        size_hint_y=None,
        height=50,
    )
    layout.add_widget(self.id_input)

    release_btn = Button(
        text='I Received Item - Release to Merchant',
        size_hint_y=None,
        height=60,
        background_color=(0.8, 0.5, 0.1, 1),
    )
    release_btn.bind(on_press=self.release_funds)
    layout.add_widget(release_btn)

    back_btn = Button(
        text='Back to Order Form',
        size_hint_y=None,
        height=50,
        background_color=(0.7, 0.2, 0.2, 1),
    )
    back_btn.bind(
        on_press=lambda x: setattr(self.manager, 'current', 'customer_screen')
    )
    layout.add_widget(back_btn)

    self.result_label = Label(
        text='Enter your booking ID after delivery',
        font_size=14,
        size_hint_y=None,
        height=40,
    )
    layout.add_widget(self.result_label)

    self.add_widget(layout)

  def release_funds(self, instance):
    b_id_str = self.id_input.text.strip()
    if not b_id_str:
      self.result_label.text = '⚠️ Please enter Booking ID!'
      return

    try:
      b_id = int(b_id_str)
    except ValueError:
      self.result_label.text = '⚠️ ID must be a number!'
      return

    conn = sqlite3.connect('p2p_escrow.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT status, amount FROM orders WHERE booking_id = ?', (b_id,)
    )
    row = cursor.fetchone()

    if not row:
      self.result_label.text = '❌ Booking ID not found!'
      conn.close()
      return

    status, amount = row
    if status == 'Completed_Released':
      self.result_label.text = 'ℹ️ Funds for this ID were already released!'
      conn.close()
      return

    cursor.execute(
        "UPDATE orders SET status = 'Completed_Released' WHERE booking_id = ?",
        (b_id,),
    )
    conn.commit()
    conn.close()

    self.result_label.text = (
        f'✅ Released {amount} LYD to Merchant Successfully!\nTransaction Closed.'
    )
    self.id_input.text = ''


# لوحة تحكم التاجر (عرض كل الطلبات والمبالغ المجمدة والمكتملة)
class AdminScreen(Screen):

  def __init__(self, **kwargs):
    super(AdminScreen, self).__init__(**kwargs)
    self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

    title = Label(
        text='Merchant Dashboard - All Orders',
        font_size=18,
        size_hint_y=None,
        height=40,
    )
    self.layout.add_widget(title)

    back_btn = Button(
        text='Back to Main Screen',
        size_hint_y=None,
        height=50,
        background_color=(0.7, 0.2, 0.2, 1),
    )
    back_btn.bind(
        on_press=lambda x: setattr(self.manager, 'current', 'customer_screen')
    )
    self.layout.add_widget(back_btn)

    self.scroll = ScrollView()
    self.orders_layout = BoxLayout(
        orientation='vertical', size_hint_y=None, spacing=10
    )
    self.orders_layout.bind(
        minimum_height=self.orders_layout.setter('height')
    )
    self.scroll.add_widget(self.orders_layout)
    self.layout.add_widget(self.scroll)

    self.add_widget(self.layout)

  def on_enter(self):
    self.load_admin_orders()

  def load_admin_orders(self):
    self.orders_layout.clear_widgets()

    conn = sqlite3.connect('p2p_escrow.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT booking_id, customer_name, product, amount, status FROM orders'
        ' ORDER BY booking_id DESC'
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
      self.orders_layout.add_widget(
          Label(text='No orders registered yet.', size_hint_y=None, height=40)
      )
      return

    for row in rows:
      b_id, name, product, amount, status = row
      # تنسيق نص العرض لكل طلب
      info_text = (
          f'ID:{b_id} | {name} | {product} | {amount}LYD\nStatus: {status}'
      )
      lbl = Label(text=info_text, font_size=12, size_hint_y=None, height=60)
      self.orders_layout.add_widget(lbl)


class EscrowApp(App):

  def build(self):
    sm = ScreenManager()
    sm.add_widget(CustomerScreen(name='customer_screen'))
    sm.add_widget(ReleaseScreen(name='release_screen'))
    sm.add_widget(AdminScreen(name='admin_screen'))
    return sm


if __name__ == '__main__':
  EscrowApp().run()
