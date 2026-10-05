import os
import pymysql

from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def get_connection():
    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        ssl={"ssl": {}},
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Sales Dashboard API is running"
    })


@app.route("/api/summary")
def summary():

    connection = get_connection()

    sql = """
    SELECT
        COUNT(*) AS records,
        SUM(quantity) AS total_quantity,
        SUM(returned_quantity) AS total_returns,
        SUM(
            (quantity - returned_quantity) * unit_price
        ) AS net_revenue
    FROM sales
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()

        # Decimal 類型轉換，方便 JSON 使用
        result["net_revenue"] = float(
            result["net_revenue"] or 0
        )

        return jsonify(result)

    finally:
        connection.close()


@app.route("/api/daily")
def daily():

    connection = get_connection()

    sql = """
    SELECT
        DATE_FORMAT(sale_date, '%%Y-%%m-%%d') AS sale_date,
        SUM(
            (quantity - returned_quantity) * unit_price
        ) AS net_revenue
    FROM sales
    GROUP BY sale_date
    ORDER BY sale_date
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        for row in rows:
            row["net_revenue"] = float(
                row["net_revenue"] or 0
            )

        return jsonify(rows)

    finally:
        connection.close()


@app.route("/api/products")
def products():

    connection = get_connection()

    sql = """
    SELECT
        product_name,
        SUM(
            (quantity - returned_quantity) * unit_price
        ) AS net_revenue
    FROM sales
    GROUP BY product_name
    ORDER BY net_revenue DESC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        for row in rows:
            row["net_revenue"] = float(
                row["net_revenue"] or 0
            )

        return jsonify(rows)

    finally:
        connection.close()


@app.route("/api/categories")
def categories():

    connection = get_connection()

    sql = """
    SELECT
        category,
        SUM(
            (quantity - returned_quantity) * unit_price
        ) AS net_revenue
    FROM sales
    GROUP BY category
    ORDER BY net_revenue DESC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        for row in rows:
            row["net_revenue"] = float(
                row["net_revenue"] or 0
            )

        return jsonify(rows)

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
