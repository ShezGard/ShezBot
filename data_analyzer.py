import logging
from typing import Dict, Any
from datetime import datetime
import pandas as pd
from config import config

logger = logging.getLogger(__name__)

def analyze_csv(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализирует CSV файл и возвращает структурированные результаты
    Возвращает:
        - Статистику по категориям (уровни 1 и 2)
        - Тренды по времени
        - Автоматические инсайты
    """
    try:
        logger.info(f"📊 Анализ данных: {len(df)} строк, {len(df.columns)} колонок")
        
        result = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "summary": {},
            "top_categories": [],
            "top_categories_level_1": [],
            "top_categories_level_2": [],
            "trends": {},
            "insights": []
        }
        
        # Автоматическое определение колонки с тематиками
        category_col = _find_category_column(df)
        date_col = _find_date_column(df)
        
        # Анализ тематик
        if category_col:
            _analyze_categories(df, category_col, result)
        
        # Анализ по дате
        if date_col:
            _analyze_dates(df, date_col, result)
        
        # Генерация инсайтов
        _generate_insights(result)
        
        logger.info("✅ Анализ данных завершён")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при анализе CSV: {e}")
        return {
            "error": str(e),
            "total_rows": len(df),
            "columns": list(df.columns)
        }

# ... остальной код анализатора без изменений ...

def _find_category_column(df: pd.DataFrame) -> str | None:
    """Находит колонку с тематиками (где есть "/" в значениях)"""
    for col in df.columns:
        sample_values = df[col].dropna().head(10)
        if any('/' in str(val) for val in sample_values):
            logger.info(f"✅ Найдена колонка с тематиками: {col}")
            return col
    
    # Если не нашли по "/", ищем по названию
    columns_lower = [str(col).lower() for col in df.columns]
    for col_name in ['тема', 'категория', 'тип', 'subject', 'category', 'type']:
        if col_name in columns_lower:
            col = df.columns[columns_lower.index(col_name)]
            logger.info(f"✅ Найдена колонка с тематиками по названию: {col}")
            return col
    
    return None

def _find_date_column(df: pd.DataFrame) -> str | None:
    """Находит колонку с датой"""
    for col in df.columns:
        sample_values = df[col].dropna().head(5)
        if any(isinstance(val, (str, pd.Timestamp, datetime)) for val in sample_values):
            try:
                pd.to_datetime(sample_values, errors='coerce')
                logger.info(f"✅ Найдена колонка с датой: {col}")
                return col
            except:
                pass
    return None

def _analyze_categories(df: pd.DataFrame, category_col: str, result: Dict) -> None:
    """Анализирует категории и их уровни"""
    df_clean = df.dropna(subset=[category_col]).copy()
    
    # Анализ по полным тематикам
    top_10_full = df_clean[category_col].value_counts().head(10)
    result["top_categories"] = [
        {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
        for name, count in top_10_full.items()
    ]
    
    # Разбор вложенных тематик
    def parse_theme_levels(theme):
        if pd.isna(theme):
            return []
        parts = str(theme).split('/')
        return [part.strip() for part in parts if part.strip()]
    
    df_clean['theme_levels'] = df_clean[category_col].apply(parse_theme_levels)
    
    # Уровень 1
    level_1 = df_clean['theme_levels'].apply(lambda x: x[0] if len(x) > 0 else 'Без категории')
    top_10_level_1 = level_1.value_counts().head(10)
    result["top_categories_level_1"] = [
        {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
        for name, count in top_10_level_1.items()
    ]
    
    # Уровень 2
    level_2 = df_clean['theme_levels'].apply(
        lambda x: f"{x[0]} / {x[1]}" if len(x) > 1 else (x[0] if len(x) > 0 else 'Без категории')
    )
    top_10_level_2 = level_2.value_counts().head(10)
    result["top_categories_level_2"] = [
        {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
        for name, count in top_10_level_2.items()
    ]
    
    # Сводка
    if len(top_10_full) > 0:
        result["summary"]["top_category"] = str(top_10_full.index[0])
        result["summary"]["top_category_count"] = int(top_10_full.iloc[0])
        result["summary"]["top_category_percent"] = round(top_10_full.iloc[0] / len(df_clean) * 100, 1)
    
    if len(top_10_level_1) > 0:
        result["summary"]["top_level_1"] = str(top_10_level_1.index[0])
    
    result["summary"]["unique_categories"] = len(level_1.unique())

def _analyze_dates(df: pd.DataFrame, date_col: str, result: Dict) -> None:
    """Анализирует данные по дате"""
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df_valid_dates = df.dropna(subset=[date_col]).copy()
        
        if len(df_valid_dates) > 0:
            result["summary"]["date_range"] = {
                "start": df_valid_dates[date_col].min().strftime('%Y-%m-%d'),
                "end": df_valid_dates[date_col].max().strftime('%Y-%m-%d'),
                "days": int((df_valid_dates[date_col].max() - df_valid_dates[date_col].min()).days)
            }
            
            # Тренд по неделям
            df_valid_dates['period'] = df_valid_dates[date_col].dt.to_period('W').astype(str)
            trend_data = df_valid_dates.groupby('period').size().to_dict()
            result["trends"]["by_week"] = trend_data
            
    except Exception as e:
        logger.warning(f"⚠️ Не удалось проанализировать даты: {e}")

def _generate_insights(result: Dict) -> None:
    """Генерирует автоматические инсайты на основе анализа"""
    top_category_percent = result["summary"].get("top_category_percent", 0)
    
    # Инсайт по основной тематике
    if top_category_percent > 50:
        result["insights"].append({
            "type": "warning",
            "message": f"ТОП-тематика '{result['summary']['top_category']}' составляет {top_category_percent}% всех обращений — это может указывать на системную проблему."
        })
    elif top_category_percent > 30:
        result["insights"].append({
            "type": "info",
            "message": f"ТОП-тематика '{result['summary']['top_category']}' составляет {top_category_percent}% — стоит обратить внимание."
        })
    
    # Инсайт по первому уровню
    if result["top_categories_level_1"]:
        top_l1 = result["top_categories_level_1"][0]
        if top_l1["percent"] > config.CRITICAL_PERCENT_THRESHOLD:
            result["insights"].append({
                "type": "warning",
                "message": f"Категория '{top_l1['name']}' составляет {top_l1['percent']}% всех обращений — возможно, нужна отдельная команда или эпик для решения."
            })
    
    # Инсайт по среднему количеству в день
    if result["summary"].get("date_range"):
        days = result["summary"]["date_range"]["days"]
        avg_per_day = result.get("total_rows", 0) / days if days > 0 else 0
        result["insights"].append({
            "type": "info",
            "message": f"Среднее количество обращений в день: {avg_per_day:.1f}"
        })

def format_data_summary(analysis: Dict) -> str:
    """Форматирует сводку данных для передачи в AI"""
    summary = f"""
📊 ОБЩАЯ СТАТИСТИКА
Всего обращений: {analysis.get('total_rows', 0)}
Уникальных категорий: {analysis['summary'].get('unique_categories', 0)}
Период анализа: {analysis['summary'].get('date_range', {}).get('start', 'N/A')} — {analysis['summary'].get('date_range', {}).get('end', 'N/A')} ({analysis['summary'].get('date_range', {}).get('days', 0)} дней)
Среднее обращений в день: {analysis['summary'].get('date_range', {}).get('days', 0) and round(analysis.get('total_rows', 0) / analysis['summary']['date_range']['days'], 1) or 'N/A'}

🏆 ТОП-10 КАТЕГОРИЙ (Уровень 1 — основные направления)
"""
    
    for i, cat in enumerate(analysis.get('top_categories_level_1', []), 1):
        summary += f"{i}. **{cat['name']}** — {cat['count']} обращений ({cat['percent']}%)\n"
    
    summary += f"\n## 📂 ТОП-10 ПОДКАТЕГОРИЙ (Уровень 2 — детализация)\n"
    
    for i, cat in enumerate(analysis.get('top_categories_level_2', []), 1):
        summary += f"{i}. **{cat['name']}** — {cat['count']} обращений ({cat['percent']}%)\n"
    
    summary += f"\n## 🎯 САМАЯ ПОПУЛЯРНАЯ ТЕМАТИКА (полная)\n"
    
    if analysis.get('top_categories'):
        top_cat = analysis['top_categories'][0]
        summary += f"**{top_cat['name']}**\n"
        summary += f"Обращений: {top_cat['count']} ({top_cat['percent']}% от общего)\n"
    
    # Добавляем инсайты
    if analysis.get('insights'):
        summary += f"\n## ⚠️ АВТОМАТИЧЕСКИЕ ИНСАЙТЫ СИСТЕМЫ:\n"
        for insight in analysis['insights']:
            summary += f"- {insight['message']}\n"
    
    summary += f"""
💡 КОНТЕКСТ ДЛЯ АНАЛИТИКА:
Это данные техподдержки по интеграции iiko с ЕГАИС и системой маркировки
Основные компоненты: ServiceApp, УТМ, плагины для iikoFront
Бизнес-воздействие: простои касс, потеря выручки, недовольство клиентов
Цель анализа: выявить системные проблемы и предложить конкретные эпики для решения
"""
    return summary

# ==================== НОВЫЕ ФУНКЦИИ: Сравнение периодов ====================

def compare_periods(analysis1: Dict, analysis2: Dict) -> Dict[str, Any]:
    """
    Сравнивает два периода и возвращает структурированные различия
    """
    try:
        logger.info("🔄 Сравнение периодов...")
        
        comparison = {
            "summary": {
                "period1_total": analysis1.get("total_rows", 0),
                "period2_total": analysis2.get("total_rows", 0),
                "total_change": 0,
                "total_change_percent": 0.0,
                "period1_unique": analysis1["summary"].get("unique_categories", 0),
                "period2_unique": analysis2["summary"].get("unique_categories", 0),
                "unique_change": 0,
                "unique_change_percent": 0.0
            },
            "category_changes": [],
            "new_categories": [],
            "disappeared_categories": [],
            "top_growers": [],
            "top_decliners": []
        }
        
        # Общее изменение
        total1 = analysis1.get("total_rows", 0)
        total2 = analysis2.get("total_rows", 0)
        
        if total1 > 0:
            comparison["summary"]["total_change"] = total2 - total1
            comparison["summary"]["total_change_percent"] = round((total2 - total1) / total1 * 100, 1)
        
        # Изменение уникальных категорий
        unique1 = analysis1["summary"].get("unique_categories", 0)
        unique2 = analysis2["summary"].get("unique_categories", 0)
        
        comparison["summary"]["unique_change"] = unique2 - unique1
        if unique1 > 0:
            comparison["summary"]["unique_change_percent"] = round((unique2 - unique1) / unique1 * 100, 1)
        
        # Сравнение категорий уровня 1
        cats1_dict = {cat["name"]: cat for cat in analysis1.get("top_categories_level_1", [])}
        cats2_dict = {cat["name"]: cat for cat in analysis2.get("top_categories_level_1", [])}
        
        all_category_names = set(cats1_dict.keys()) | set(cats2_dict.keys())
        
        for cat_name in all_category_names:
            cat1 = cats1_dict.get(cat_name)
            cat2 = cats2_dict.get(cat_name)
            
            if cat1 and cat2:
                # Категория есть в обоих периодах
                change = cat2["count"] - cat1["count"]
                change_percent = round((cat2["count"] - cat1["count"]) / cat1["count"] * 100, 1) if cat1["count"] > 0 else 0
                
                comparison["category_changes"].append({
                    "name": cat_name,
                    "period1_count": cat1["count"],
                    "period2_count": cat2["count"],
                    "change": change,
                    "change_percent": change_percent,
                    "period1_percent": cat1["percent"],
                    "period2_percent": cat2["percent"],
                    "trend": "up" if change > 0 else "down" if change < 0 else "same"
                })
            elif cat1 and not cat2:
                # Категория исчезла
                comparison["disappeared_categories"].append({
                    "name": cat_name,
                    "period1_count": cat1["count"],
                    "period1_percent": cat1["percent"]
                })
            elif not cat1 and cat2:
                # Новая категория
                comparison["new_categories"].append({
                    "name": cat_name,
                    "period2_count": cat2["count"],
                    "period2_percent": cat2["percent"]
                })
        
        # ТОП-5 роста
        comparison["top_growers"] = sorted(
            [c for c in comparison["category_changes"] if c["trend"] == "up"],
            key=lambda x: x["change_percent"],
            reverse=True
        )[:5]
        
        # ТОП-5 падения
        comparison["top_decliners"] = sorted(
            [c for c in comparison["category_changes"] if c["trend"] == "down"],
            key=lambda x: x["change_percent"]
        )[:5]
        
        logger.info("✅ Сравнение периодов завершено")
        return comparison
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при сравнении периодов: {e}")
        return {"error": str(e)}

def format_comparison_summary(comparison: Dict, analysis1: Dict, analysis2: Dict) -> str:
    """Форматирует сводку сравнения для передачи в AI"""
    summary = f"""
📊 СРАВНЕНИЕ ПЕРИОДОВ

📈 ОБЩАЯ ДИНАМИКА
Обращений в периоде 1: {comparison['summary']['period1_total']}
Обращений в периоде 2: {comparison['summary']['period2_total']}
Изменение: {comparison['summary']['total_change']} ({comparison['summary']['total_change_percent']}%)
Уникальных категорий в периоде 1: {comparison['summary']['period1_unique']}
Уникальных категорий в периоде 2: {comparison['summary']['period2_unique']}
Изменение категорий: {comparison['summary']['unique_change']} ({comparison['summary']['unique_change_percent']}%)

🏆 ТОП-5 КАТЕГОРИЙ С НАИБОЛЬШИМ РОСТОМ
"""
    
    for i, cat in enumerate(comparison.get("top_growers", []), 1):
        trend = "↗️" if cat["change_percent"] > 0 else "↘️"
        summary += f"{i}. **{cat['name']}** — {cat['period1_count']} → {cat['period2_count']} ({cat['change']} / {cat['change_percent']}%) {trend}\n"
    
    summary += f"\n📉 ТОП-5 КАТЕГОРИЙ С НАИБОЛЬШИМ ПАДЕНИЕМ\n"
    
    for i, cat in enumerate(comparison.get("top_decliners", []), 1):
        trend = "↗️" if cat["change_percent"] > 0 else "↘️"
        summary += f"{i}. **{cat['name']}** — {cat['period1_count']} → {cat['period2_count']} ({cat['change']} / {cat['change_percent']}%) {trend}\n"
    
    if comparison.get("new_categories"):
        summary += f"\n🆕 НОВЫЕ КАТЕГОРИИ (появились во 2 периоде)\n"
        for cat in comparison["new_categories"]:
            summary += f"- **{cat['name']}** — {cat['period2_count']} обращений ({cat['period2_percent']}%)\n"
    
    if comparison.get("disappeared_categories"):
        summary += f"\n❌ ИСЧЕЗНУВШИЕ КАТЕГОРИИ (были в 1 периоде, нет во 2)\n"
        for cat in comparison["disappeared_categories"]:
            summary += f"- **{cat['name']}** — было {cat['period1_count']} обращений ({cat['period1_percent']}%)\n"
    
    summary += f"""
💡 КОНТЕКСТ ДЛЯ АНАЛИТИКА:
Это сравнение данных техподдержки по интеграции iiko с ЕГАИС и системой маркировки
Период 1 → Период 2: что изменилось, какие проблемы усилились/ослабли
Цель анализа: выявить тренды, новые проблемы и успехи команды
"""
    return summary