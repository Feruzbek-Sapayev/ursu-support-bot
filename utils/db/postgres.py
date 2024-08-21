from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone_number VARCHAR(25)    
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        applications INT DEFAULT 0,
        rating INT DEFAULT 0
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_applications(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Applications (
        id SERIAL PRIMARY KEY,
        applicant INT NOT NULL,
        files TEXT NOT NULL,
        status VARCHAR(25) NOT NULL DEFAULT 'Yangi',
        admin BIGINT,
        created TIMESTAMP NOT NULL, 
        group_message TEXT 
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_chat(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Chat (
        id SERIAL PRIMARY KEY,
        application INT NOT NULL,
        messages TEXT
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id, phone_number):
        sql = "INSERT INTO users (full_name, username, telegram_id,phone_number) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, username, telegram_id, phone_number, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)


    # applications
    async def add_application(self, applicant, files, status, admin, created, group_message):
            sql = "INSERT INTO Applications (applicant, files, status, admin, created, group_message) VALUES($1, $2, $3, $4, $5, $6) returning *"
            return await self.execute(sql, applicant, files, status, admin, created, group_message, fetchrow=True)
    
    async def select_application(self, **kwargs):
        sql = "SELECT * FROM Applications WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def select_applications(self, **kwargs):
        sql = "SELECT * FROM Applications WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def update_application_status(self, status, admin, app_id):
        sql = "UPDATE Applications SET status=$1, admin=$2 WHERE id=$3"
        return await self.execute(sql, status, admin, app_id, execute=True)
    
    async def update_application_group_message(self, group_message, app_id):
        sql = "UPDATE Applications SET group_message=$1 WHERE id=$2"
        return await self.execute(sql, group_message, app_id, execute=True)
    

    # admins
    async def add_admin(self, full_name, username, telegram_id, applications, rating):
        sql = "INSERT INTO Admins (full_name, username, telegram_id, applications, rating) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, full_name, username, telegram_id, applications, rating, fetchrow=True)

    async def select_all_admins(self):
        sql = "SELECT * FROM Admins"
        return await self.execute(sql, fetch=True)

    async def select_admin(self, **kwargs):
        sql = "SELECT * FROM Admins WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def update_admin_status(self, application, telegram_id):
        sql = "UPDATE Admins SET applications=$1 WHERE telegram_id=$2"
        return await self.execute(sql, application, telegram_id, execute=True)
    
    async def update_admin_stars(self, rating, telegram_id):
        sql = "UPDATE Admins SET rating=$1 WHERE telegram_id=$2"
        return await self.execute(sql, rating, telegram_id, execute=True)
    

    
    # chat
    async def add_message_to_chat(self, application, messages):
        sql = "INSERT INTO Chat (application, messages) VALUES($1, $2) returning *"
        return await self.execute(sql, application, messages, fetchrow=True)
    
    async def select_chat_message(self, **kwargs):
        sql = "SELECT * FROM Chat WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def update_chat_message(self, messages, application):
        sql = "UPDATE Chat SET messages=$1 WHERE application=$2"
        return await self.execute(sql, messages, application, execute=True)