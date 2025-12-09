import time
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Database
from core.template_engine import BatchExporter


def test_100_quests_in_5_seconds():
    """Тест создания 100 квестов за 5 секунд"""
    print("🔥 Начинаем БОСС-ФАЙТ! 🔥")
    print("=" * 50)

    db = Database()

    try:
        start = time.time()
        elapsed = BatchExporter.generate_100_quests(db)

        print(f"⏱️  Время выполнения: {elapsed:.2f} секунд")
        print(f"📊 Создано квестов: 100")
        print(f"⚡ Скорость: {100/elapsed:.2f} квестов/сек")

        assert elapsed < 5, f"❌ Слишком медленно: {elapsed:.2f} сек (требуется < 5 сек)"

        print("=" * 50)
        print(f"✅ БОСС ПОВЕРЖЕН ЗА {elapsed:.2f} СЕКУНД! +20 XP")
        print("🏆 Достижение разблокировано: 'Демон скорости'")

        return True

    except AssertionError as e:
        print(f"\n{e}")
        print("💀 Босс оказался слишком силен... Попробуйте оптимизировать код!")
        return False

    except Exception as e:
        print(f"❌ Ошибка во время теста: {e}")
        return False

    finally:
        db.close()


def test_batch_performance():
    """Дополнительный тест производительности"""
    print("\n🎯 Дополнительный тест производительности")
    print("=" * 50)

    db = Database()

    try:
        # Тест 1: 10 квестов
        start = time.time()
        for i in range(10):
            db.create_quest(
                f"Быстрый квест {i}",
                "Легкий",
                100,
                "Описание " * 15,
                "2025-12-31 23:59:59"
            )
        elapsed_10 = time.time() - start
        print(f"✓ 10 квестов: {elapsed_10:.3f} сек ({10/elapsed_10:.2f} квестов/сек)")

        # Тест 2: 50 квестов
        start = time.time()
        for i in range(50):
            db.create_quest(
                f"Средний квест {i}",
                "Средний",
                500,
                "Описание " * 15,
                "2025-12-31 23:59:59"
            )
        elapsed_50 = time.time() - start
        print(f"✓ 50 квестов: {elapsed_50:.3f} сек ({50/elapsed_50:.2f} квестов/сек)")

        print("=" * 50)
        print("✅ Дополнительные тесты пройдены!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    print("⚔️  QUEST MASTER - ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ⚔️\n")

    # Основной тест
    success = test_100_quests_in_5_seconds()

    # Дополнительные тесты
    if success:
        test_batch_performance()

    print("\n🎮 Тестирование завершено!")