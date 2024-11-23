import os
import xrpl
import json
import tkinter as tk
import tkinter.font as tk_font
from server import Server
from verifier import Verifier
from app import Application

host_seed = os.getenv("HOST_SEED", "sEdVbSUqosrj4AJKQCV9aq8dKmeY2a6")  # Seed of the host
guest_seed = xrpl.core.keypairs.generate_seed()  # Generate a random seed for the guest

server = Server(host_seed)  # Server that registers and books the guest

palace = Verifier(None, server.wallet.address)  # Palace (structure) that the guest wants to enter
application: Application = None  # Application of the guest (initialized after registration)


def register() -> None:
    global server, guest_seed, application
    global text_1, text_2, ent_guest  # GUI
    import datetime
    # Register the guest to the services
    guest_address, nft = server.register(
        guest_seed,
        str(datetime.datetime(year=2024, month=11, day=21, hour=14, tzinfo=datetime.timezone.utc)),
        str(datetime.datetime(year=2024, month=11, day=24, hour=10, tzinfo=datetime.timezone.utc)),
        {"1":True, "2": False, "3": False}
    )
    application = Application(guest_seed)  # Initialize the application of the guest
    uri = json.loads(bytes.fromhex(nft["URI"]))
    text_1.delete("1.0", tk.END)
    text_2.delete("1.0", tk.END)
    txt = f"Registered Guest: {guest_address}\nNFT: {json.dumps(nft, indent=4)}\nURI: {json.dumps(uri, indent=4)}"
    text_1.insert("1.0", txt)
    text_2.insert("1.0", "You are now registered!")
    ent_guest.insert(0, guest_address)


def open_palace() -> None:
    global application, palace
    global text_2  # GUI
    if application is None:
        text_2.delete("1.0", tk.END)
        text_2.insert("1.0", "You need to register!")
        return
    proof = application.authenticate(None)
    result = palace.verify(application.wallet.address, proof)
    text_2.delete("1.0", tk.END)
    if result:
        text_2.insert("1.0", "You can enter the palace!")
    else:
        text_2.insert("1.0", "You shall not pass!")


def check_service(service_id: str) -> None:
    global application, server
    global text_2  # GUI
    if application is None:
        text_2.delete("1.0", tk.END)
        text_2.insert("1.0", "You need to register!")
        return
    verifier = Verifier(service_id, server.wallet.address)
    proof = application.authenticate(service_id)
    result = verifier.verify(application.wallet.address, proof)
    text_2.delete("1.0", tk.END)
    if result:
        text_2.insert("1.0", f"You can use service {service_id}!")
    else:
        text_2.insert("1.0", f"You cannot use service {service_id}!")


# Create the main window
window = tk.Tk()
window.title("GUI Example")
extra_large_font = tk_font.Font(size=18, weight="bold", slant="italic")
large_font = tk_font.Font(size=13, weight="bold")
medium_font = tk_font.Font(size=11)

# Top left corner: Guest and Host entries
frm_left = tk.Frame(window)
frm_left.pack(side=tk.LEFT, padx=10, pady=10)

lbl_guest = tk.Label(master=frm_left, text="Guest:", font=large_font)
ent_guest = tk.Entry(master=frm_left, width=50, font=medium_font)
lbl_host = tk.Label(master=frm_left, text="Host:", font=large_font)
ent_host = tk.Entry(master=frm_left, width=50, font=medium_font)
ent_host.insert(0, server.wallet.address)

lbl_guest.grid(row=1, column=0, sticky="w", pady=5)
ent_guest.grid(row=1, column=1, pady=5)
lbl_host.grid(row=0, column=0, sticky="w", pady=5)
ent_host.grid(row=0, column=1, pady=5)

# Top right corner: Buttons
frm_right = tk.Frame(window)
frm_right.pack(side=tk.RIGHT, padx=10, pady=10)

btn_register = tk.Button(master=frm_right, text="Register", command=register, font=large_font)
btn_open_palace = tk.Button(master=frm_right, text="Open Palace", command=open_palace, font=large_font)
btn_service_1 = tk.Button(master=frm_right, text="Service 1", command=lambda: check_service("1"), font=large_font)
btn_service_2 = tk.Button(master=frm_right, text="Service 2", command=lambda: check_service("2"), font=large_font)
btn_service_3 = tk.Button(master=frm_right, text="Service 3", command=lambda: check_service("3"), font=large_font)

btn_register.grid(row=0, column=0, padx=5, pady=5)
btn_open_palace.grid(row=1, column=0, padx=5, pady=5)
btn_service_1.grid(row=2, column=0, padx=5, pady=5)
btn_service_2.grid(row=3, column=0, padx=5, pady=5)
btn_service_3.grid(row=4, column=0, padx=5, pady=5)

# Bottom: Text areas
frm_bottom = tk.Frame(window)
frm_bottom.pack(side=tk.BOTTOM, padx=10, pady=10)

text_1 = tk.Text(master=frm_bottom, height=30, width=101, font=medium_font)
text_2 = tk.Text(master=frm_bottom, height=3, width=62, font=extra_large_font)

text_1.pack(padx=5, pady=5)
text_2.pack(padx=5, pady=5)

# Start the application
window.mainloop()
