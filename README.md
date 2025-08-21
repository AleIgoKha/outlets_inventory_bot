# Outlets Inventory Application

<p align="center">
  <img src="https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/outlets_inventory_bot_logo.jpeg" width="200">
</p>

<!-- ![Logo](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/outlets_inventory_bot_logo.jpeg) -->

## Stack
![Python](https://img.shields.io/badge/-Python-1d1717?style=for-the-badge&logo=Python&logoColor=fff6f6)
![Aiogram](https://img.shields.io/badge/-Aiogram-1d1717?style=for-the-badge&logo=Aiogram&logoColor=fff6f6)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-1d1717?style=for-the-badge&logo=PostgreSQL&logoColor=fff6f6)
![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-1d1717?style=for-the-badge&logo=SQLAlchemy&logoColor=fff6f6)
![Redis](https://img.shields.io/badge/-Redis-1d1717?style=for-the-badge&logo=Redis&logoColor=fff6f6)
![Docker](https://img.shields.io/badge/-Docker-1d1717?style=for-the-badge&logo=Docker&logoColor=fff6f6)
![Alembic](https://img.shields.io/badge/-Alembic-1d1717?style=for-the-badge&logo=Alembic&logoColor=fff6f6)

## Description

This bot application is designed for tracking goods at retail outlets. Its unique feature is that it functions as a chat with a single message and instant auto-deletion of user inputs. This makes it feel like a full-fledged application rather than just a bot. The implementation and workflow for product accounting are optimized for our needs.

## Project Goals

- Collect data and monitor changes in product quantities at retail outlets.
- Control sellers responsible for product sales at retail outlets.

## How It Works 

In the app, you choose a retail outlet and its current inventory.

![choosing_product](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/choosing_product.png)

Inventory is managed through three operations: replenishment, write-off, and balance.

**Replenishment**\
Increases product stock (recorded immediately upon arrival).

![replenishment_menu](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/replenishment_menu.PNG)

**Write-off**\
Decreases product stock (due to defects, losses, etc.).

![writeoff_menu](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/writeoff_menu.PNG)

**Balance**\
A daily check-in of current stock levels. Daily sales are calculated as the difference, taking into account all operations.

![balance_menu](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/balance_menu.PNG)

**Report**  
At the end of the day, a report is filled in: remaining stock, actual revenue, number of transactions, and comments. The report can only be submitted once. After submission, the responsible person receives a summary with key indicators, including the difference between actual and calculated revenue.

![report_menu](https://github.com/AleIgoKha/outlets_inventory_bot/blob/main/assets/reporting.png)

The collected data is then used to build dashboards: sales analysis, supply planning, and production prioritization. You can find them and the SQL queries they based on [here in this repository](https://github.com/AleIgoKha/superset_queries_and_dashboards/tree/main).