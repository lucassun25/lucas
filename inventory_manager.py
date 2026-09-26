#!/usr/bin/env python3
"""命令行库存管理器。

功能：添加、删除、搜索商品，更新库存，并将数据保存到 JSON 文件。
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DATA_FILE = Path("inventory.json")


@dataclass
class Product:
    """表示一件库存商品。"""

    product_id: int
    name: str
    category: str
    price: float
    quantity: int

    def stock_value(self) -> float:
        return self.price * self.quantity


class Inventory:
    """负责商品的增删改查和持久化。"""

    def __init__(self, file_path: Path = DATA_FILE) -> None:
        self.file_path = file_path
        self.products: dict[int, Product] = {}
        self.load()

    def load(self) -> None:
        """从 JSON 文件读取库存；文件不存在时从空库存开始。"""
        if not self.file_path.exists():
            return

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            self.products = {
                int(item["product_id"]): Product(**item) for item in data
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise RuntimeError(f"无法读取库存文件：{error}") from error

    def save(self) -> None:
        """将库存写入 JSON 文件。"""
        data = [asdict(product) for product in self.products.values()]
        self.file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, product: Product) -> None:
        if product.product_id in self.products:
            raise ValueError(f"商品编号 {product.product_id} 已存在")
        self.products[product.product_id] = product
        self.save()

    def remove(self, product_id: int) -> Product:
        try:
            product = self.products.pop(product_id)
        except KeyError as error:
            raise ValueError(f"找不到商品编号 {product_id}") from error
        self.save()
        return product

    def update_quantity(self, product_id: int, amount: int) -> Product:
        product = self.get(product_id)
        new_quantity = product.quantity + amount
        if new_quantity < 0:
            raise ValueError("库存数量不能小于 0")
        product.quantity = new_quantity
        self.save()
        return product

    def get(self, product_id: int) -> Product:
        try:
            return self.products[product_id]
        except KeyError as error:
            raise ValueError(f"找不到商品编号 {product_id}") from error

    def search(self, keyword: str) -> list[Product]:
        keyword = keyword.casefold()
        return [
            product
            for product in self.products.values()
            if keyword in product.name.casefold()
            or keyword in product.category.casefold()
        ]

    def low_stock(self, threshold: int) -> list[Product]:
        return sorted(
            (product for product in self.products.values() if product.quantity <= threshold),
            key=lambda product: product.quantity,
        )

    def total_value(self) -> float:
        return sum(product.stock_value() for product in self.products.values())


def format_products(products: Iterable[Product]) -> str:
    products = list(products)
    if not products:
        return "没有找到匹配的商品。"

    lines = ["编号   商品名称              分类          单价       数量       库存价值"]
    lines.append("-" * 76)
    for product in sorted(products, key=lambda item: item.product_id):
        lines.append(
            f"{product.product_id:<6}{product.name:<22}{product.category:<14}"
            f"¥{product.price:<9.2f}{product.quantity:<11}¥{product.stock_value():.2f}"
        )
    return "\n".join(lines)


def positive_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("必须是非负整数")
    return number


def positive_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("必须是非负数")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="库存管理器")
    parser.add_argument("--file", type=Path, default=DATA_FILE, help="JSON 数据文件路径")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="添加商品")
    add_parser.add_argument("id", type=positive_int, help="商品编号")
    add_parser.add_argument("name", help="商品名称")
    add_parser.add_argument("category", help="商品分类")
    add_parser.add_argument("price", type=positive_float, help="商品单价")
    add_parser.add_argument("quantity", type=positive_int, help="初始库存")

    remove_parser = subparsers.add_parser("remove", help="删除商品")
    remove_parser.add_argument("id", type=positive_int)

    update_parser = subparsers.add_parser("update", help="调整库存")
    update_parser.add_argument("id", type=positive_int)
    update_parser.add_argument("amount", type=int, help="增加或减少的数量，例如 -2")

    search_parser = subparsers.add_parser("search", help="按名称或分类搜索")
    search_parser.add_argument("keyword")

    low_parser = subparsers.add_parser("low-stock", help="查看低库存商品")
    low_parser.add_argument("threshold", type=positive_int, nargs="?", default=5)

    subparsers.add_parser("list", help="列出全部商品")
    subparsers.add_parser("summary", help="查看库存汇总")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        inventory = Inventory(args.file)

        if args.command == "add":
            inventory.add(Product(args.id, args.name, args.category, args.price, args.quantity))
            print(f"已添加商品：{args.name}")
        elif args.command == "remove":
            removed = inventory.remove(args.id)
            print(f"已删除商品：{removed.name}")
        elif args.command == "update":
            product = inventory.update_quantity(args.id, args.amount)
            print(f"{product.name} 的当前库存为 {product.quantity}")
        elif args.command == "search":
            print(format_products(inventory.search(args.keyword)))
        elif args.command == "low-stock":
            print(format_products(inventory.low_stock(args.threshold)))
        elif args.command == "list":
            print(format_products(inventory.products.values()))
        elif args.command == "summary":
            print(f"商品种类：{len(inventory.products)}")
            print(f"商品总数：{sum(p.quantity for p in inventory.products.values())}")
            print(f"库存总价值：¥{inventory.total_value():.2f}")
    except (ValueError, RuntimeError) as error:
        print(f"错误：{error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
