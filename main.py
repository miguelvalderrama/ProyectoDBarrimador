import sqlite3
from tkinter import *
from tkinter import ttk
import datetime
import time
from ttkwidgets.autocomplete import AutocompleteCombobox


create = sqlite3.connect('arrimadores.db')

create.execute(""" CREATE TABLE IF NOT EXISTS arrimadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    animal TEXT NOT NULL, 
                    cantidad INTEGER NOT NULL,  
                    kg FLOAT NOT NULL,
                    Nliq TEXT,
                    date DATE NOT NULL
                    )""")

names = []

############################################################################################
# Functions
############################################################################################
def button_ing():
    nb.select(tab1)
    nb.hide(tab2)
    nb.hide(tab3)

def button_res():
    nb.select(tab2)
    nb.hide(tab1)
    nb.hide(tab3)

def button_opc():
    nb.select(tab3)
    nb.hide(tab2)
    nb.hide(tab1)

def ingresar(name, animal, cantidad, kg):
    if not name or not animal or not cantidad or not kg:
        return False
    #Get date from system
    date = datetime.datetime.now()
    date = date.strftime("%d/%m/%Y")

    #For each cantidad, insert into database
    for i in range(int(cantidad)):
        create.execute("INSERT INTO arrimadores (name, animal, cantidad, kg, date) VALUES (?,?,?,?,?)", (name, animal, 1, kg, date))
    create.commit()
    
    #Clear entrys
    entry_name.delete(0, END)
    combo_cantidad.delete(0, END)
    combo_animal.delete(0, END)
    spin_kg.delete(0, END)

    #Update table
    update_table()

def update_table(date_initial=None, date_final=None):
    #Get date from system
    date = datetime.datetime.now()
    date = date.strftime("%d/%m/%Y")

    #Get data from database
    if date_initial and date_final:
        data = create.execute("SELECT id, name, animal, kg, date FROM arrimadores WHERE date BETWEEN ? AND ?", (date_initial, date_final))
    else:
        data = create.execute("SELECT id, name, animal, kg, date FROM arrimadores")
    #Delete all rows
    tree.delete(*tree.get_children())
    #Insert data into table and sort by descending id (newest first)
    for row in sorted(data, key=lambda x: x[0], reverse=True):
        tree.insert("", END, values=row)
    
    #Update name list
    update_name_list()

    #Update totals 
    update_totals_of_animals_and_kg()

def update_name_list():
    #Get global name list
    global names
    #Get data from database
    data = create.execute("SELECT DISTINCT name FROM arrimadores")
    #Delete names data
    names.clear()
    #Insert data into list
    for row in data:
        names.append(row[0])

def update_totals_of_animals_and_kg():
    #Get data from database
    data = create.execute("SELECT animal, kg FROM arrimadores WHERE date BETWEEN ? AND ?", (entry_date.get(), entry_date_end.get()))
    #Delete data
    animals = {}
    kg = 0
    #Insert data into dictionary
    for row in data:
        if row[0] in animals:
            animals[row[0]] += 1
        else:
            animals[row[0]] = 1
        kg += row[1]
    #Update labels
    lbl_total_animals_value.config(text=str(sum(animals.values())))
    lbl_total_kg_value.config(text=str('{:.2f}'.format(kg)))


def delete_row(id):
    create.execute("DELETE FROM arrimadores WHERE id = ?", (id,))
    create.commit()
    update_table()
    #Update name list
    update_name_list()
    #Close popper window

def edit_row(id, name, animal, kg):
    #Update database
    create.execute("UPDATE arrimadores SET name = ?, animal = ?, kg = ? WHERE id = ?", (name, animal, kg, id))
    create.commit()
    #Update table
    update_table()

def select_row(event):
    #Get selected row
    selected_row = tree.selection()[0]
    #Get data from selected row
    data = tree.item(selected_row, "values")
    #Pop a window with data
    pop_window(data)

def pop_window_try(data):    #Try function
    #Create window
    window = Toplevel()
    window.title("Arrimador")
    window.geometry("400x200")
    window.resizable(0,0)
    print(data)

def pop_window(data):
    #Create window
    popper = Toplevel()
    popper.title("Arrimador")
    popper.geometry("400x200")
    popper.resizable(0,0)
    #Create labels
    label_id = Label(popper, text="ID: ")
    label_name = Label(popper, text="Nombre: ")
    label_animal = Label(popper, text="Animal: ")
    label_kg = Label(popper, text="Kg: ")
    label_date = Label(popper, text="Fecha: ")
    #Create entrys
    entry_id = Entry(popper, width=28)
    entry_name = Entry(popper, width=28)
    entry_animal = ttk.Combobox(popper, width=25, values=('Vaca', 'Toro', 'Bufalo', 'Bufala'))
    entry_kg = Entry(popper, width=28)
    entry_date = Entry(popper, width=28)
    #Insert data into entrys
    entry_id.insert(0, data[0])
    entry_id.config(state="readonly")
    entry_name.insert(0, data[1])
    entry_animal.insert(0, data[2])
    entry_kg.insert(0, data[3])
    entry_date.insert(0, data[4])
    entry_date.config(state="readonly")
    #Create buttons
    button_delete = Button(popper, text="Eliminar", command=lambda:[delete_row(data[0]), popper.destroy()])
    button_edit = Button(popper, text="Editar", command=lambda: [edit_row(data[0], entry_name.get(), entry_animal.get(), entry_kg.get()) , popper.destroy()])
    #Create grid
    label_id.grid(row=0, column=0)
    entry_id.grid(row=0, column=1)
    label_name.grid(row=1, column=0)
    entry_name.grid(row=1, column=1)
    label_animal.grid(row=2, column=0)
    entry_animal.grid(row=2, column=1)
    label_kg.grid(row=3, column=0)
    entry_kg.grid(row=3, column=1)
    label_date.grid(row=4, column=0)
    entry_date.grid(row=4, column=1)
    button_delete.place(x=50, y=120)
    button_edit.place(x=200, y=120)

def pop_window_submit(cantidad):
    #Create window
    submit = Toplevel()
    submit.title("Arrimadores")
    submit.geometry("300x500")
    submit.resizable(0,0)
    #Create labels
    Label(submit, text="Nº Liq: ").grid(row=0, column=0)
    Label(submit, text="Kg: ").grid(row=0, column=1)
    
    #Create entrys
    for element in range(cantidad):
        entry_liquidation = Entry(submit, width=20)
        entry_kg = Entry(submit, width=20)
        entry_liquidation.grid(row=element+1, column=0)
        entry_kg.grid(row=element+1, column=1)
        entry_liquidation.insert(0, 0)
        entry_kg.insert(0, 0)

    #Create buttons
    button_submit = Button(submit, text="Enviar")
    button_submit.grid(row=cantidad+1, column=0)


############################################################################################
#Main
############################################################################################
#Create a window
window = Tk()
window.title("Arrimadores")
window.geometry('1024x500')
window.resizable(0,0)

#Create a sidebar
sidebar = Frame(window, width=150, height=500, bg='#2E2E2E')
sidebar.grid(row=0, column=0, sticky='n')

#Create a container for the main content
container = Frame(window, width=874, height=500)
container.grid(row=0, column=1, sticky='n')

#Create a notebook
nb = ttk.Notebook(container, width=874, height=500)
nb.pack(fill=BOTH, expand=1)

#Create a tab
tab1 = ttk.Frame(nb)
nb.add(tab1, text='Ingreso')

tab2 = ttk.Frame(nb)
nb.add(tab2, text='Resumen')

tab3 = ttk.Frame(nb)
nb.add(tab3, text='Opciones')

#Hide
nb.hide(tab1)
nb.hide(tab2)
nb.hide(tab3)

#Create buttons
btn_ing = Button(sidebar, text='Ingreso', command=button_ing, bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12))
btn_ing.place(x=0, y=35)

btn_res = Button(sidebar, text='Resumen', command=button_res, bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12))
btn_res.place(x=0, y=75)

btn_opc = Button(sidebar, text='Opciones', command=button_opc, bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12))
btn_opc.place(x=0, y=400)

################################
# Tab1 Ingreso
################################
#Create labels
lbl_name = Label(tab1, text='Nombre:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_name.place(x=30, y=50)

lbl_cantidad = Label(tab1, text='Cantidad:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_cantidad.place(x=170, y=50)

lbl_animal = Label(tab1, text='Animal:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_animal.place(x=30, y=125)

lbl_kg = Label(tab1, text='Kg:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_kg.place(x=170, y=125)

update_name_list()

#Create entry
entry_name = AutocompleteCombobox(tab1, width=16, completevalues=names)
entry_name.place(x=30, y=70)

combo_cantidad = Spinbox(tab1, from_=1, to=10, width=18)
combo_cantidad.place(x=170, y=70)

#Create combobox
combo_animal = ttk.Combobox(tab1, values=('Vaca', 'Toro', 'Bufalo', 'Bufala'), width=16)
combo_animal.place(x=30, y=150)

#Create spinbox
spin_kg = Spinbox(tab1, from_=0, to=100, width=18)
spin_kg.place(x=170, y=150)

#Events for entry
entry_name.bind('<Return>', lambda event: combo_cantidad.focus())
combo_cantidad.bind('<Return>', lambda event: combo_animal.focus())
combo_animal.bind('<Return>', lambda event: spin_kg.focus())
spin_kg.bind('<Return>', button_ing())

#Create buttons
btn_ingresar = Button(tab1, text='Guardar', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12), command=lambda: ingresar(entry_name.get(), combo_animal.get(), combo_cantidad.get(), spin_kg.get()))
btn_ingresar.place(x=75, y=350)

#Date
lbl_date = Label(tab1, text='Fecha:', bg='#2E2E2E', fg='#FFFFFF', width=12, relief=FLAT, font=('Arial', 10))
lbl_date.place(x=400, y=400)
lbl_date_end = Label(tab1, text='Hasta:', bg='#2E2E2E', fg='#FFFFFF', width=12, relief=FLAT, font=('Arial', 10))
lbl_date_end.place(x=550, y=400)

#Initial date entry
date_ini = StringVar()
date_ini.set(time.strftime("%d/%m/%Y"))
#End date
date_end = StringVar()
date_end.set(time.strftime("%d/%m/%Y"))

#Create entry for date
entry_date = Entry(tab1, textvariable=date_ini, width=16)
entry_date.place(x=400, y=425)
entry_date_end = Entry(tab1, textvariable=date_end, width=16)
entry_date_end.place(x=550, y=425)

#Create buttons
btn_date = Button(tab1, text='Buscar', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12), command=lambda: update_table(date_ini.get(), date_end.get()))
btn_date.place(x=680, y=400)


#Create a table in the right side
tree = ttk.Treeview(tab1, columns=('id','name', 'animal', 'kg', 'date'), height=14)
tree.heading('#0', text='', anchor=W)
tree.heading('#1', text='ID', anchor=CENTER)
tree.heading('#2', text='Nombre', anchor=CENTER)
tree.heading('#3', text='Animal', anchor=CENTER)
tree.heading('#4', text='Kg', anchor=CENTER)
tree.heading('#5', text='Fecha', anchor=CENTER)
tree.column('#0', stretch=NO, minwidth=0, width=0)
tree.column('#1', stretch=NO, minwidth=0, width=0)
tree.column('#2', stretch=NO, minwidth=0, width=100)
tree.column('#3', stretch=NO, minwidth=0, width=100)
tree.column('#4', stretch=NO, minwidth=0, width=100)
tree.column('#5', stretch=NO, minwidth=0, width=100)
tree.place(x=400, y=30)

#Total of animals and kg
lbl_total_animals = Label(tab1, text='Total de animales:', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_animals.place(x=420, y=340)
lbl_total_kg = Label(tab1, text='Total de kg:', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_kg.place(x=420, y=370)

#Total of animals and kg
lbl_total_animals_value = Label(tab1, text='0', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_animals_value.place(x=550, y=340)
lbl_total_kg_value = Label(tab1, text='0', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_kg_value.place(x=550, y=370)

update_totals_of_animals_and_kg()


#Create a scrollbar for the table
scrollbar = Scrollbar(tab1, orient="vertical", command=tree.yview, width=20)
scrollbar.place(x=800, y=30, height=310)

#Update table
update_table()

#Select row in table
tree.bind('<Double-1>', lambda event: select_row(tree))

################################
# Tab2 Resumen
################################

#Create labels
lbl_name2 = Label(tab2, text='Nombre:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_name2.place(x=30, y=50)

lbl_animal2 = Label(tab2, text='Animal:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_animal2.place(x=30, y=125)

lbl_filter = Label(tab2, text='Filtro:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_filter.place(x=170, y=125)

#Create entry
entry_name2 = AutocompleteCombobox(tab2, width=16, completevalues=names)
entry_name2.place(x=30, y=70)

#Create combobox
combo_animal2 = ttk.Combobox(tab2, values=('Todos', 'Vaca', 'Toro', 'Bufalo', 'Bufala'), width=16)
combo_animal2.set('Todos')
combo_animal2.place(x=30, y=150)

#Create spinbox
combo_filter = ttk.Combobox(tab2, values=('Kg: Mayor a menor', 'Kg: Menor a mayor', 'Cant: Mayor a menor', 'Cant: Menor a mayor'), width=16)
combo_filter.set('Cant: Mayor a menor')
combo_filter.place(x=170, y=150)

#Events for entrys

#Create buttons
btn_buscar = Button(tab2, text='Buscar', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12))
btn_buscar.place(x=75, y=350)

#Date
lbl_date2 = Label(tab2, text='Fecha:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_date2.place(x=30, y=200 )
lbl_date_end2 = Label(tab2, text='Hasta:', bg='#2E2E2E', fg='#FFFFFF', width=14, relief=FLAT, font=('Arial', 10))
lbl_date_end2.place(x=170, y=200)

#Initial date entry
date_ini2 = StringVar()
date_ini2.set(time.strftime("%d/%m/%Y"))
#End date
date_end2 = StringVar()
date_end2.set(time.strftime("%d/%m/%Y"))

#Create entry for date
entry_date2 = Entry(tab2, textvariable=date_ini, width=18)
entry_date2.place(x=30, y=225)
entry_date_end2 = Entry(tab2, textvariable=date_end, width=18)
entry_date_end2.place(x=170, y=225)

#Create buttons
#btn_date = Button(tab1, text='Buscar', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 12), command=lambda: update_table(date_ini.get(), date_end.get()))
#btn_date.place(x=680, y=400)


#Create a table in the right side
tree2 = ttk.Treeview(tab2, columns=('id','name', 'animal','Cantidad', 'kg', 'date'), height=14)
tree2.heading('#0', text='', anchor=W)
tree2.heading('#1', text='ID', anchor=CENTER)
tree2.heading('#2', text='Nombre', anchor=CENTER)
tree2.heading('#3', text='Animal', anchor=CENTER)
tree2.heading('#4', text='Cantidad', anchor=CENTER)
tree2.heading('#5', text='Kg', anchor=CENTER)
tree2.heading('#6', text='Fecha', anchor=CENTER)
tree2.column('#0', stretch=NO, minwidth=0, width=0)
tree2.column('#1', stretch=NO, minwidth=0, width=0)
tree2.column('#2', stretch=NO, minwidth=0, width=100)
tree2.column('#3', stretch=NO, minwidth=0, width=100)
tree2.column('#4', stretch=NO, minwidth=0, width=100)
tree2.column('#5', stretch=NO, minwidth=0, width=100)
tree2.column('#6', stretch=NO, minwidth=0, width=100)
tree2.place(x=300, y=30)

#Total of animals and kg
lbl_total_animals2 = Label(tab2, text='Total de animales:', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_animals2.place(x=420, y=340)
lbl_total_kg2 = Label(tab2, text='Total de kg:', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_kg2.place(x=420, y=370)

#Total of animals and kg
lbl_total_animals_value2 = Label(tab2, text='0', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_animals_value2.place(x=550, y=340)
lbl_total_kg_value2 = Label(tab2, text='0', bg='#2E2E2E', fg='#FFFFFF', width=16, relief=FLAT, font=('Arial', 10))
lbl_total_kg_value2.place(x=550, y=370)

#update_totals_of_animals_and_kg()


#Create a scrollbar for the table
scrollbar2 = Scrollbar(tab2, orient="vertical", command=tree.yview, width=20)
scrollbar2.place(x=800, y=30, height=310)

#Update table

################################

############################################################################################


pop_window_submit(3)
window.mainloop()