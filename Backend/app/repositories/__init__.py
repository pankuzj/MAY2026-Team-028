"""Repositories — the only layer that talks to the database.

CRUD + queries returning ORM objects/primitives. No business rules, no HTTP.

# TODO: one repository per aggregate (complaint, bulk_pickup, task, user, ...).
"""
