import pandas as pd
import numpy as np
import math
from scipy.stats import t


def get_initial_graphs_data(product):
    product_data = product.consumptiondata_set.all()
    code = product.code
    desc = product.description
    ven = product.ven
    price = product.price
    current_stock = product.currentStock
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr:
        value = data_np_arr.mean()
        return dict([('code', code), ('description', desc),('ven',ven),
                     ('price',price),('current_stock',current_stock),('stat', value)])


def more_graphs_data(product,stat):
    product_data = product.consumptiondata_set.all()
    code = product.code
    desc = product.description
    ven = product.ven
    price = product.price
    planned_qty_2_month_mean = product.planned_Qty_2Month_Mean
    current_stock = product.currentStock
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr:
        if stat == "mean":
            value = data_np_arr.mean()
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock), ('stat', value)])
        elif stat == "sum":
            value = data_np_arr.sum()
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])
        elif stat == "price":
            value = price
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])
        elif stat == "planned_Qty_2Month_Mean":
            value = planned_qty_2_month_mean
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])
        elif stat == "months_of_stock":
            value = len(data_np_arr)
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])
        elif stat == "current_stock":
            value = current_stock
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])
        else:
            value = data_np_arr.mean()
            return dict([('code', code), ('description', desc), ('ven', ven),
                         ('current_stock',current_stock),('stat', value)])


def get_graphs_2_consumption_data(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr != []:
        p_sum = data_np_arr.sum()
        p_mean = data_np_arr.mean()
        p_length = len(data_np_arr)
        x2 = []
        for value in data_np_arr:
            x2.append(pow(value, 2))

        x2_np_arr = np.array(x2)
        x2_sum = x2_np_arr.sum()
        square_n = (pow(p_sum, 2)) / (p_length)
        if p_length == 1:
            std_error = 0
        else:
            var = ((x2_sum) - (square_n)) / (p_length - 1)
            std = np.sqrt(var)
            std_error = np.float(std) / np.sqrt(p_length)

        pb_t_test = 0.95
        df = p_length - 1
        t_statistic = t.ppf(pb_t_test, df)
        confidence_interval = t_statistic * std_error
        deviation_from_mean = (confidence_interval / float(p_mean)) * 100
        code = product.code
        desc = product.description
        ven = product.ven
        plannedQty2Month_order_cost = product.price * product.planned_Qty_2Month_Mean
        planned_Qty_Month_Mean = product.planned_Qty_2Month_Mean / 2
        plannedQtyMonth_order_cost = product.price * planned_Qty_Month_Mean
        annual_plan_cost = plannedQtyMonth_order_cost * 12
        percentage_change_in_consumption = deviation_from_mean
        amc_in_packs = float(p_mean)
        no_of_stock_outs = 0
        amc_adjusted_for_stock_outs = amc_in_packs / (1 - (no_of_stock_outs / 30.5))
        amc_adjusted_for_changes = amc_adjusted_for_stock_outs * (1 + (percentage_change_in_consumption / 100))
        safety_stock = amc_adjusted_for_changes * 1
        qty_to_procure = amc_adjusted_for_changes * (1 + 2) + safety_stock
        calculated_2Month_qty_to_procure = qty_to_procure
        calculated_2Month_cost_of_procurement = calculated_2Month_qty_to_procure * float(product.price)
        calculated_2_month_cycle_cost_of_procurement_in_millions = calculated_2Month_cost_of_procurement/1000000
        budget_deficit_in_plan = calculated_2Month_cost_of_procurement - float(plannedQty2Month_order_cost)
        if calculated_2Month_cost_of_procurement != 0:
            percentage_available_funding = float(plannedQty2Month_order_cost) / (
                    calculated_2Month_cost_of_procurement / 100)
        else:
            percentage_available_funding = np.nan

        if stat == "planned_Qty_2Month_Mean":
            value = product.planned_Qty_2Month_Mean
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "planned_Qty_Month_Mean":
            value = planned_Qty_Month_Mean
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "plannedQtyMonth_order_cost":
            value = plannedQtyMonth_order_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "plannedQty2Month_order_cost":
            value = plannedQty2Month_order_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_plan_cost":
            value = annual_plan_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_change_in_consumption":
            value = percentage_change_in_consumption
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "amc_adjusted_for_stock_outs":
            value = amc_adjusted_for_stock_outs
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "amc_adjusted_for_changes":
            value = amc_adjusted_for_changes
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "safety_stock":
            value = safety_stock
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "calculated_2Month_qty_to_procure":
            value = calculated_2Month_qty_to_procure
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "calculated_2_month_cycle_cost_of_procurement_in_millions":
            value = calculated_2_month_cycle_cost_of_procurement_in_millions
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "budget_deficit_in_plan":
            value = budget_deficit_in_plan
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_available_funding":
            value = percentage_available_funding
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        else:
            value = data_np_arr.mean()
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])


def get_graphs_3_consumption_data(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr != []:
        p_sum = data_np_arr.sum()
        p_mean = data_np_arr.mean()
        p_length = len(data_np_arr)
        x2 = []
        for value in data_np_arr:
            x2.append(pow(value, 2))

        x2_np_arr = np.array(x2)
        x2_sum = x2_np_arr.sum()
        square_n = (pow(p_sum, 2)) / (p_length)
        if p_length == 1:
            std_error = 0
        else:
            var = ((x2_sum) - (square_n)) / (p_length - 1)
            std = np.sqrt(var)
            std_error = np.float(std) / np.sqrt(p_length)

        pb_t_test = 0.95
        df = p_length - 1
        t_statistic = t.ppf(pb_t_test, df)
        confidence_interval = t_statistic * std_error
        deviation_from_mean = (confidence_interval / float(p_mean)) * 100
        code = product.code
        desc = product.description
        ven = product.ven
        planned_qty_month_mean = product.planned_Qty_2Month_Mean / 2
        planned_qty_3_month_mean = planned_qty_month_mean * 3
        planned_qty_3_month_order_cost = float(planned_qty_3_month_mean) * float(product.price)
        annual_plan_cost = planned_qty_3_month_order_cost * 4
        amc_in_packs = float(p_mean)
        no_of_stock_outs = 0
        amc_adjusted_for_stock_outs = amc_in_packs / (1 - (no_of_stock_outs / 30.5))
        percentage_change_in_consumption = deviation_from_mean
        amc_adjusted_for_changes = amc_adjusted_for_stock_outs * (1 + (percentage_change_in_consumption / 100))
        safety_stock = amc_adjusted_for_changes * 1.5
        qty_to_procure = amc_adjusted_for_changes * (1.5 + 3) + safety_stock
        calculated_3_month_qty_to_procure = qty_to_procure
        calculated_3_month_cycle_cost_of_procurement = calculated_3_month_qty_to_procure * float(product.price)
        calculated_3_month_cycle_cost_of_procurement_in_millions = calculated_3_month_cycle_cost_of_procurement/1000000
        budget_deficit_in_plan = calculated_3_month_cycle_cost_of_procurement - float(planned_qty_3_month_order_cost)
        if calculated_3_month_cycle_cost_of_procurement != 0:
            percentage_available_funding = float(planned_qty_3_month_order_cost) / (
                    calculated_3_month_cycle_cost_of_procurement / 100)
        else:
            percentage_available_funding = np.nan

        if stat == "planned_qty_3_month_mean":
            value = planned_qty_3_month_mean
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "planned_qty_month_mean":
            value = planned_qty_month_mean
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "planned_qty_3_month_order_cost":
            value = planned_qty_3_month_order_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_plan_cost":
            value = annual_plan_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_change_in_consumption":
            value = percentage_change_in_consumption
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "amc_adjusted_for_stock_outs":
            value = amc_adjusted_for_stock_outs
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "amc_adjusted_for_changes":
            value = amc_adjusted_for_changes
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "safety_stock":
            value = safety_stock
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "calculated_3_month_qty_to_procure":
            value = calculated_3_month_qty_to_procure
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "calculated_3_month_cycle_cost_of_procurement_in_millions":
            value = calculated_3_month_cycle_cost_of_procurement_in_millions
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "budget_deficit_in_plan":
            value = budget_deficit_in_plan
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_available_funding":
            value = percentage_available_funding
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        else:
            value = data_np_arr.mean()
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])


def get_graphs_2_eoq_data(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr != []:
        p_sum = data_np_arr.sum()
        p_mean = data_np_arr.mean()
        p_length = len(data_np_arr)
        x2 = []
        for value in data_np_arr:
            x2.append(pow(value, 2))

        x2_np_arr = np.array(x2)
        x2_sum = x2_np_arr.sum()
        square_n = (pow(p_sum, 2)) / (p_length)
        if p_length == 1:
            std_error = 0
        else:
            var = ((x2_sum) - (square_n)) / (p_length - 1)
            std = np.sqrt(var)
            std_error = np.float(std) / np.sqrt(p_length)

        pb_t_test = 0.95
        df = p_length - 1
        t_statistic = t.ppf(pb_t_test, df)
        confidence_interval = t_statistic * std_error
        deviation_from_mean = (confidence_interval / float(p_mean)) * 100
        code = product.code
        desc = product.description
        ven = product.ven
        planned_Qty_Month_Mean = product.planned_Qty_2Month_Mean / 2
        plannedQtyMonth_order_cost = product.price * planned_Qty_Month_Mean
        annual_plan_cost = plannedQtyMonth_order_cost * 12
        percentage_change_in_consumption = deviation_from_mean
        amc_in_packs = float(p_mean)
        no_of_stockouts = 0
        amc_adjusted_for_stockouts = amc_in_packs / (1 - (no_of_stockouts / 30.5))
        amc_adjusted_for_changes = amc_adjusted_for_stockouts * (1 + (percentage_change_in_consumption / 100))

        year_demand = amc_adjusted_for_changes * 12
        carrying_cost = float(product.price) * 0.12
        ordering_cost = float(product.price) * 0.04

        if carrying_cost == 0:
            economic_order_quantity = np.nan
        else:
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost) / carrying_cost))

        annual_carrying_cost = economic_order_quantity / 2 * carrying_cost
        annual_ordering_cost = year_demand / economic_order_quantity * ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        annual_demand_cost = year_demand * float(product.price)
        length_of_order_cycle_days = economic_order_quantity / year_demand * 365
        number_cycles_per_year = 365 / length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(product.price)
        investment_cost_per_year = investment_cost_per_cycle * number_cycles_per_year
        annual_total_cost = investment_cost_per_year + annual_inventory_mgt_cost
        percentage_inventory_mgt_cost = annual_inventory_mgt_cost / (annual_total_cost / 100)
        plan_budget_deficit = annual_total_cost - float(annual_plan_cost)
        percentage_available__funding = float(annual_plan_cost) / (annual_total_cost / 100)
        if stat == "year_demand":
            value = year_demand
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "carrying_cost":
            value = carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "ordering_cost":
            value = ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "economic_order_quantity":
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_carrying_cost":
            value = annual_carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_ordering_cost":
            value = annual_ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_inventory_mgt_cost":
            value = annual_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_demand_cost":
            value = annual_demand_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "length_of_order_cycle_days":
            value = length_of_order_cycle_days
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "number_cycles_per_year":
            value = number_cycles_per_year
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "investment_cost_per_cycle":
            value = investment_cost_per_cycle
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "investment_cost_per_year":
            value = investment_cost_per_year
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_total_cost":
            value = annual_total_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_inventory_mgt_cost":
            value = percentage_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "plan_budget_deficit":
            value = plan_budget_deficit
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_available__funding":
            value = percentage_available__funding
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        else:
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])


def get_graphs_3_eoq_data(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr != []:
        p_sum = data_np_arr.sum()
        p_mean = data_np_arr.mean()
        p_length = len(data_np_arr)
        x2 = []
        for value in data_np_arr:
            x2.append(pow(value, 2))

        x2_np_arr = np.array(x2)
        x2_sum = x2_np_arr.sum()
        square_n = (pow(p_sum, 2)) / (p_length)
        if p_length == 1:
            std_error = 0
        else:
            var = ((x2_sum) - (square_n)) / (p_length - 1)
            std = np.sqrt(var)
            std_error = np.float(std) / np.sqrt(p_length)

        pb_t_test = 0.95
        df = p_length - 1
        t_statistic = t.ppf(pb_t_test, df)
        confidence_interval = t_statistic * std_error
        deviation_from_mean = (confidence_interval / float(p_mean)) * 100
        code = product.code
        desc = product.description
        ven = product.description
        planned_qty_month_mean = product.planned_Qty_2Month_Mean / 2
        planned_qty_3_month_mean = planned_qty_month_mean * 3
        planned_qty_3_month_order_cost = float(planned_qty_3_month_mean) * float(product.price)
        annual_plan_cost = planned_qty_3_month_order_cost * 4
        amc_in_packs = float(p_mean)
        no_of_stock_outs = 0
        amc_adjusted_for_stock_outs = amc_in_packs / (1 - (no_of_stock_outs / 30.5))
        percentage_change_in_consumption = deviation_from_mean
        amc_adjusted_for_changes = amc_adjusted_for_stock_outs * (1 + (percentage_change_in_consumption / 100))
        safety_stock = amc_adjusted_for_changes * 1.5
        qty_to_procure = amc_adjusted_for_changes * (1.5 + 3) + safety_stock
        calculated_3_month_qty_to_procure = qty_to_procure
        year_demand = calculated_3_month_qty_to_procure * 4
        carrying_cost = float(product.price) * 0.12
        ordering_cost = float(product.price) * 0.04
        if carrying_cost == 0:
            economic_order_quantity = np.nan
        else:
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost) / carrying_cost))

        annual_carrying_cost = economic_order_quantity / 2 * carrying_cost
        annual_ordering_cost = year_demand / economic_order_quantity * ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        annual_demand_cost = year_demand * float(product.price)
        length_of_order_cycle_days = economic_order_quantity / year_demand * 365
        number_cycles_per_year = 365 / length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(product.price)
        investment_cost_per_year = investment_cost_per_cycle * number_cycles_per_year
        annual_total_cost = investment_cost_per_year + annual_inventory_mgt_cost
        percentage_inventory_mgt_cost = annual_inventory_mgt_cost / (annual_total_cost / 100)
        plan_budget_deficit = annual_total_cost - float(annual_plan_cost)
        percentage_available__funding = float(annual_plan_cost) / (annual_total_cost / 100)
        if stat == "year_demand":
            value = year_demand
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "carrying_cost":
            value = carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "ordering_cost":
            value = ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "economic_order_quantity":
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_carrying_cost":
            value = annual_carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_ordering_cost":
            value = annual_ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_inventory_mgt_cost":
            value = annual_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_demand_cost":
            value = annual_demand_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "length_of_order_cycle_days":
            value = length_of_order_cycle_days
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "number_cycles_per_year":
            value = number_cycles_per_year
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "investment_cost_per_cycle":
            value = investment_cost_per_cycle
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "investment_cost_per_year":
            value = investment_cost_per_year
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "annual_total_cost":
            value = annual_total_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_inventory_mgt_cost":
            value = percentage_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "plan_budget_deficit":
            value = plan_budget_deficit
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        elif stat == "percentage_available__funding":
            value = percentage_available__funding
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])
        else:
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven), ('stat', value)])