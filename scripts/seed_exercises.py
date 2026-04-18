import asyncio
from sqlalchemy import select
from src.infrastructure.db.session import async_session_factory
from src.infrastructure.db.models import ExerciseModel

exercises_data = [
    {
        "name": "Жим штанги лежа",
        "primary_muscle_group": "Грудь",
        "secondary_muscle_groups": ["Передняя дельта", "Трицепс"],
        "description": "Базовое упражнение для развития мышц груди. Выполняется лежа на горизонтальной скамье.",
        "biomechanics_tags": ["базовое", "жим", "горизонтальная плоскость"]
    },
    {
        "name": "Приседания со штангой",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": ["Ягодицы", "Разгибатели спины"],
        "description": "Фундаментальное упражнение для нижней части тела. Штанга на плечах, присед до параллели.",
        "biomechanics_tags": ["базовое", "ноги", "коленный доминант"]
    },
    {
        "name": "Подтягивания",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Бицепс", "Предплечья"],
        "description": "Классическое упражнение с собственным весом для развития широчайших мышц спины.",
        "biomechanics_tags": ["базовое", "тяга", "вертикальная плоскость"]
    },
    {
        "name": "Становая тяга",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Ноги", "Ягодицы", "Трапеции"],
        "description": "Одно из самых эффективных упражнений для развития общей силы и массы спины.",
        "biomechanics_tags": ["базовое", "тяга", "тазово-доминантное"]
    },
    {
        "name": "Армейский жим",
        "primary_muscle_group": "Плечи",
        "secondary_muscle_groups": ["Трицепс", "Верх груди"],
        "description": "Жим штанги над головой стоя. Развивает передние и средние дельты.",
        "biomechanics_tags": ["базовое", "жим", "вертикальная плоскость"]
    },
    {
        "name": "Подъем штанги на бицепс",
        "primary_muscle_group": "Бицепс",
        "secondary_muscle_groups": ["Предплечья"],
        "description": "Классическое изолирующее упражнение для двуглавой мышцы плеча.",
        "biomechanics_tags": ["изоляция", "руки"]
    },
    {
        "name": "Французский жим",
        "primary_muscle_group": "Трицепс",
        "secondary_muscle_groups": [],
        "description": "Разгибание рук со штангой из-за головы лежа. Акцент на длинную головку трицепса.",
        "biomechanics_tags": ["изоляция", "руки"]
    },
    {
        "name": "Планка",
        "primary_muscle_group": "Пресс",
        "secondary_muscle_groups": ["Кора", "Плечи"],
        "description": "Статическое упражнение для укрепления мышц кора.",
        "biomechanics_tags": ["статика", "кора"]
    },
    {
        "name": "Выпады с гантелями",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": ["Ягодицы"],
        "description": "Шаги вперед с гантелями в руках. Отличное упражнение для проработки бедер.",
        "biomechanics_tags": ["базовое", "ноги", "унилатеральное"]
    },
    {
        "name": "Тяга штанги в наклоне",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Задняя дельта", "Бицепс"],
        "description": "Тяга штанги к поясу в наклоне для толщины спины.",
        "biomechanics_tags": ["базовое", "тяга", "горизонтальная плоскость"]
    },
    {
        "name": "Махи гантелями в стороны",
        "primary_muscle_group": "Плечи",
        "secondary_muscle_groups": [],
        "description": "Изолирующее упражнение для средней дельты.",
        "biomechanics_tags": ["изоляция", "плечи"]
    },
    {
        "name": "Скручивания",
        "primary_muscle_group": "Пресс",
        "secondary_muscle_groups": [],
        "description": "Классическое упражнение на мышцы пресса на полу.",
        "biomechanics_tags": ["изоляция", "пресс"]
    },
    {
        "name": "Жим ногами",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": ["Ягодицы"],
        "description": "Жим платформы ногами в тренажере. Позволяет работать с большими весами.",
        "biomechanics_tags": ["базовое", "ноги", "тренажер"]
    },
    {
        "name": "Гиперэкстензия",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Ягодицы", "Бицепс бедра"],
        "description": "Разгибание спины в специальном тренажере. Укрепляет поясницу.",
        "biomechanics_tags": ["изоляция", "спина", "поясница"]
    },
    {
        "name": "Тяга верхнего блока",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Бицепс"],
        "description": "Имитация подтягиваний в блочном тренажере.",
        "biomechanics_tags": ["базовое", "тяга", "тренажер"]
    },
    {
        "name": "Отжимания на брусьях",
        "primary_muscle_group": "Грудь",
        "secondary_muscle_groups": ["Трицепс", "Передняя дельта"],
        "description": "Отличное упражнение с весом тела для низа груди и трицепса.",
        "biomechanics_tags": ["базовое", "жим", "вертикальная плоскость"]
    },
    {
        "name": "Мертвая тяга",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": ["Ягодицы", "Разгибатели спины"],
        "description": "Тяга на прямых ногах. Основной акцент на бицепс бедра и ягодицы.",
        "biomechanics_tags": ["базовое", "ноги", "тазово-доминантное"]
    },
    {
        "name": "Жим гантелей лежа",
        "primary_muscle_group": "Грудь",
        "secondary_muscle_groups": ["Трицепс", "Передняя дельта"],
        "description": "Вариация жима лежа, позволяющая увеличить амплитуду движения.",
        "biomechanics_tags": ["базовое", "жим", "гантели"]
    },
    {
        "name": "Разводка гантелей лежа",
        "primary_muscle_group": "Грудь",
        "secondary_muscle_groups": [],
        "description": "Изолирующее упражнение для растяжки и проработки грудных мышц.",
        "biomechanics_tags": ["изоляция", "грудь"]
    },
    {
        "name": "Подъем ног в висе",
        "primary_muscle_group": "Пресс",
        "secondary_muscle_groups": ["Подвздошно-поясничная"],
        "description": "Сложное упражнение для мышц нижнего пресса.",
        "biomechanics_tags": ["изоляция", "пресс"]
    },
    {
        "name": "Тяга горизонтального блока",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Бицепс", "Задняя дельта"],
        "description": "Тяга к поясу сидя в блочном тренажере.",
        "biomechanics_tags": ["базовое", "тяга", "тренажер"]
    },
    {
        "name": "Молотки с гантелями",
        "primary_muscle_group": "Бицепс",
        "secondary_muscle_groups": ["Брахиалис", "Предплечья"],
        "description": "Подъемы гантелей нейтральным хватом.",
        "biomechanics_tags": ["изоляция", "руки"]
    },
    {
        "name": "Сведение рук в кроссовере",
        "primary_muscle_group": "Грудь",
        "secondary_muscle_groups": [],
        "description": "Изолирующее упражнение в кроссовере для детализации груди.",
        "biomechanics_tags": ["изоляция", "грудь", "тренажер"]
    },
    {
        "name": "Разгибание ног в тренажере",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": [],
        "description": "Изоляция для квадрицепса.",
        "biomechanics_tags": ["изоляция", "ноги", "тренажер"]
    },
    {
        "name": "Сгибание ног в тренажере",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": [],
        "description": "Изоляция для бицепса бедра.",
        "biomechanics_tags": ["изоляция", "ноги", "тренажер"]
    },
    {
        "name": "Подъем на носки стоя",
        "primary_muscle_group": "Ноги",
        "secondary_muscle_groups": ["Икры"],
        "description": "Упражнение для развития икроножных мышц.",
        "biomechanics_tags": ["изоляция", "ноги", "икры"]
    },
    {
        "name": "Шраги со штангой",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Трапеции"],
        "description": "Подъем плеч со штангой для развития верхних трапеций.",
        "biomechanics_tags": ["изоляция", "трапеции"]
    },
    {
        "name": "Обратные отжимания",
        "primary_muscle_group": "Трицепс",
        "secondary_muscle_groups": ["Передняя дельта"],
        "description": "Отжимания от скамьи сзади.",
        "biomechanics_tags": ["базовое", "трицепс"]
    },
    {
        "name": "Концентрированный подъем на бицепс",
        "primary_muscle_group": "Бицепс",
        "secondary_muscle_groups": [],
        "description": "Подъем гантели сидя с упором локтя в бедро.",
        "biomechanics_tags": ["изоляция", "бицепс"]
    },
    {
        "name": "Жим штанги узким хватом",
        "primary_muscle_group": "Трицепс",
        "secondary_muscle_groups": ["Грудь", "Передняя дельта"],
        "description": "Базовое упражнение для трицепса, выполняемое на горизонтальной скамье.",
        "biomechanics_tags": ["базовое", "жим", "трицепс"]
    },
    {
        "name": "Тяга гантели в наклоне",
        "primary_muscle_group": "Спина",
        "secondary_muscle_groups": ["Бицепс", "Задняя дельта"],
        "description": "Тяга гантели к поясу одной рукой с упором о скамью.",
        "biomechanics_tags": ["базовое", "тяга", "унилатеральное"]
    },
    {
        "name": "Разгибание рук на блоке",
        "primary_muscle_group": "Трицепс",
        "secondary_muscle_groups": [],
        "description": "Изолирующее упражнение на верхнем блоке для проработки трицепса.",
        "biomechanics_tags": ["изоляция", "трицепс", "тренажер"]
    },
    {
        "name": "Подъем гантелей перед собой",
        "primary_muscle_group": "Плечи",
        "secondary_muscle_groups": [],
        "description": "Изолирующее упражнение для передней дельты.",
        "biomechanics_tags": ["изоляция", "плечи"]
    },
    {
        "name": "Махи гантелями в наклоне",
        "primary_muscle_group": "Плечи",
        "secondary_muscle_groups": ["Спина"],
        "description": "Упражнение для проработки задней дельты.",
        "biomechanics_tags": ["изоляция", "плечи", "задняя дельта"]
    },
    {
        "name": "Жим гантелей сидя",
        "primary_muscle_group": "Плечи",
        "secondary_muscle_groups": ["Трицепс"],
        "description": "Базовое упражнение для развития дельтовидных мышц.",
        "biomechanics_tags": ["базовое", "жим", "плечи"]
    }
]

async def seed_exercises():
    async with async_session_factory() as session:
        for exercise in exercises_data:
            # Проверяем, существует ли упражнение
            stmt = select(ExerciseModel).where(ExerciseModel.name == exercise["name"])
            result = await session.execute(stmt)
            existing_exercise = result.scalar_one_or_none()

            if existing_exercise:
                print(f"Упражнение '{exercise['name']}' уже существует. Пропускаем.")
                continue

            new_exercise = ExerciseModel(
                name=exercise["name"],
                primary_muscle_group=exercise["primary_muscle_group"],
                secondary_muscle_groups=exercise["secondary_muscle_groups"],
                description=exercise["description"],
                biomechanics_tags=exercise["biomechanics_tags"]
            )
            session.add(new_exercise)
            print(f"Добавлено упражнение: {exercise['name']}")

        await session.commit()
        print("База данных успешно заполнена упражнениями.")

if __name__ == "__main__":
    asyncio.run(seed_exercises())
