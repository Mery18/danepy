# -*- coding: utf-8 -*-

import os
from peewee import *
from dane import *

baza_plik = "pracownicy.sqlite3"
if os.path.exists(baza_plik):
    os.remove(baza_plik)
# tworzymy instancję bazy używanej przez modele
baza = SqliteDatabase(baza_plik)  # ':memory:'


class BazaModel(Model):  # klasa bazowa
    class Meta:
        database = baza


class Dzial(BazaModel):
    id = IntegerField(primary_key=True)
    nazwa = CharField(null=False)
    siedziba = CharField(null=False)


class Premia(BazaModel):
    id = CharField(primary_key=True)
    premia = DecimalField()


class Pracownik(BazaModel):
    id = CharField(primary_key=True)
    nazwisko = CharField(null=False)
    imie = CharField(null=False)
    stanowisko = ForeignKeyField(Premia, related_name='pracownicy')
    data_zatr = CharField(null=False)
    placa = DecimalField(decimal_places=2)
    premia = DecimalField(decimal_places=2, default=0)
    id_dzial = ForeignKeyField(Dzial, related_name='pracownicy')


baza.connect()  # nawiązujemy połączenie z bazą
baza.create_tables([Dzial, Premia, Pracownik], True)  # tworzymy tabele

dzial = [dict(zip(Dzial._meta.sorted_field_names, row)) for row in dzial]
premia = [dict(zip(Premia._meta.sorted_field_names, row)) for row in premia]
pracownicy = [dict(zip(Pracownik._meta.sorted_field_names, row))
              for row in pracownicy]


with baza.atomic():
    Dzial.insert_many(dzial).execute()
    Premia.insert_many(premia).execute()
    for idx in range(0, len(pracownicy), 100):
        Pracownik.insert_many(pracownicy[idx:idx + 100]).execute()

# zob. http://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts


def kw_c():
    query = (Dzial
             .select(Dzial.siedziba, fn.Sum(Pracownik.placa).alias('place'))
             .join(Pracownik)
             .group_by(Dzial.siedziba)
             .order_by('place').asc())

    for row in query:
        print(row.siedziba, row.place)


def kw_d():
    query = (Pracownik
             .select(Dzial.id, Dzial.nazwa, Pracownik.nazwisko, Pracownik.imie)
             .join(Dzial)
             .order_by(Dzial.nazwa).asc())

    for row in query:
        print(row.id_dzial.id, row.id_dzial.nazwa, row.nazwisko, row.imie)


query = (Pracownik
         .select()
         .where(Pracownik.imie.endswith('a')))
for row in query:
    print(row.imie)
# zob.: https://stackoverflow.com/questions/20589462/string-matching-in-peewee-sql
