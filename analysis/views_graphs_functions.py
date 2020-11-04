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


def get_graphs_consumption_method_1_month_cycle(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    ven = product.ven
    price = float(product.price)
    current_stock = product.currentStock
    planned_qty_2_month_mean = float(product.planned_Qty_2Month_Mean)
    planned_qty_1_month_mean = planned_qty_2_month_mean / 2
    planned_qty_1_month_order_cost = price * planned_qty_1_month_mean
    planned_qty_1_month_order_cost_thousands = planned_qty_1_month_order_cost / 1000
    annual_plan_cost = planned_qty_1_month_order_cost * 12
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

        amc = float(p_mean)
        amc_in_packs = amc
        no_of_stock_outs = 0
        amc_adjusted_for_stock_outs = amc_in_packs / (1 - (no_of_stock_outs / 30.5))
        if deviation_from_mean != 0:
            percentage_change_in_consumption = deviation_from_mean
        else:
            percentage_change_in_consumption = np.nan

        min_amc = amc_in_packs*((100 - percentage_change_in_consumption)/100)
        max_amc = amc_in_packs*((100 + percentage_change_in_consumption)/100)
        poisson_mode_quantity = round(amc_in_packs)
        poisson_mode_qty_adjusted_for_changes_in_use = poisson_mode_quantity
        safety_stock = poisson_mode_qty_adjusted_for_changes_in_use * 0.5
        qty_to_procure = poisson_mode_qty_adjusted_for_changes_in_use * (0.5+1) + safety_stock
        eff_qty_to_procure = qty_to_procure
        calc_1_month_cycle_qty_to_procure_adjusted_for_losses = eff_qty_to_procure
        calculated_1_month_cycle_cost_of_procurement = price * calc_1_month_cycle_qty_to_procure_adjusted_for_losses
        calculated_1_month_cycle_cost_of_procurement_thousand = calculated_1_month_cycle_cost_of_procurement/1000
        consumption_annual_procurement_cost = 12 * calculated_1_month_cycle_cost_of_procurement
        budget_deficit_in_plan = calculated_1_month_cycle_cost_of_procurement - float(planned_qty_1_month_order_cost)
        if calculated_1_month_cycle_cost_of_procurement != 0:
            percentage_available_funding = float(planned_qty_1_month_order_cost) / (
                    calculated_1_month_cycle_cost_of_procurement / 100)
        else:
            percentage_available_funding = 0

        if stat == "planned_Qty_2Month_Mean":
            value = planned_qty_2_month_mean
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "planned_Qty_Month_Mean":
            value = planned_qty_1_month_mean
            return dict([('code', code), ('description', desc), ('ven', ven), ("PRICE",price),
                         ("current_stock",current_stock),('stat', value)])
        elif stat == "plannedQtyMonth_order_cost":
            value = planned_qty_1_month_order_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "planned_qty_1_month_order_cost_thousands":
            value = planned_qty_1_month_order_cost_thousands
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_plan_cost":
            value = annual_plan_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "amc_in_packs":
            value = amc_in_packs
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "amc_adjusted_for_stock_outs":
            value = amc_adjusted_for_stock_outs
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "percentage_change_in_consumption":
            value = percentage_change_in_consumption
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "min_amc":
            value = min_amc
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "max_amc":
            value = max_amc
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "poisson_mode_quantity":
            value = poisson_mode_quantity
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "safety_stock":
            value = safety_stock
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "eff_qty_to_procure":
            value = eff_qty_to_procure
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "calculated_1_month_cycle_cost_of_procurement":
            value = calculated_1_month_cycle_cost_of_procurement
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "calculated_1_month_cycle_cost_of_procurement_thousand":
            value = calculated_1_month_cycle_cost_of_procurement_thousand
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "consumption_annual_procurement_cost":
            value = consumption_annual_procurement_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "budget_deficit_in_plan":
            value = budget_deficit_in_plan
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "percentage_available_funding":
            value = percentage_available_funding
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        else:
            value = amc_in_packs
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])


def get_graphs_eoq_model_1_month_cycle(product, stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    ven = product.ven
    price = float(product.price)
    current_stock = product.currentStock
    planned_qty_2_month_mean = product.planned_Qty_2Month_Mean
    planned_qty_1_month_mean = planned_qty_2_month_mean / 2
    planned_qty_1_month_mean = float(planned_qty_1_month_mean)
    planned_qty_1_month_order_cost = price * planned_qty_1_month_mean
    annual_plan_cost = planned_qty_1_month_order_cost * 12
    if arr != []:
        p_mean = data_np_arr.mean()
        amc = float(p_mean)
        amc_in_packs = amc
        poisson_mode_quantity = round(amc_in_packs)
        year_demand = poisson_mode_quantity * 12
        carrying_cost = float(price) * 0.12
        ordering_cost = float(price) * 0.04
        if carrying_cost == 0:
            economic_order_quantity = np.nan
        else:
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost) / carrying_cost))
        annual_carrying_cost = economic_order_quantity / 2 * carrying_cost
        annual_ordering_cost = year_demand / economic_order_quantity * ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        annual_demand_cost = year_demand * float(price)
        length_of_order_cycle_days = economic_order_quantity / year_demand * 365
        number_cycles_per_year = 365 / length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(price)
        annual_investment_cost = number_cycles_per_year * investment_cost_per_cycle
        annual_investment_cost_millions = annual_investment_cost / 1000000
        annual_total_cost = annual_investment_cost + annual_inventory_mgt_cost
        annual_total_cost_millions = annual_total_cost / 1000000
        percentage_annual_inventory_mgt_cost_per_demand_cost = annual_inventory_mgt_cost / (annual_total_cost / 100)
        plan_budget_deficit = float(annual_plan_cost) - float(annual_investment_cost)
        percentage_available_funding = float(annual_plan_cost) / (float(annual_investment_cost) / 100)
        if stat == "year_demand":
            value = year_demand
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "carrying_cost":
            value = carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "ordering_cost":
            value = ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "economic_order_quantity":
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_carrying_cost":
            value = annual_carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_ordering_cost":
            value = annual_ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_inventory_mgt_cost":
            value = annual_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_demand_cost":
            value = annual_demand_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "length_of_order_cycle_days":
            value = length_of_order_cycle_days
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "number_cycles_per_year":
            value = number_cycles_per_year
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "investment_cost_per_cycle":
            value = investment_cost_per_cycle
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_investment_cost":
            value = annual_investment_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_investment_cost_millions":
            value = annual_investment_cost_millions
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_total_cost":
            value = annual_total_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "annual_total_cost_millions":
            value = annual_total_cost_millions
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "percentage_annual_inventory_mgt_cost_per_demand_cost":
            value = percentage_annual_inventory_mgt_cost_per_demand_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "plan_budget_deficit":
            value = plan_budget_deficit
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "percentage_available_funding":
            value = percentage_available_funding
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        else:
            value = economic_order_quantity
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])


def get_graphs_standardised_consumption_plan_1_week_cycle(product,stat):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    ven = product.ven
    price = float(product.price)
    current_stock = product.currentStock
    planned_qty_2_month_mean = product.planned_Qty_2Month_Mean
    planned_qty_1_month_mean = planned_qty_2_month_mean / 2
    planned_qty_1_month_mean = float(planned_qty_1_month_mean)
    planned_qty_1_month_order_cost = price * planned_qty_1_month_mean
    if arr != []:
        p_mean = data_np_arr.mean()

        amc = float(p_mean)
        amc_in_packs = amc
        poisson_mode_quantity = round(amc_in_packs)
        year_demand = poisson_mode_quantity * 12
        carrying_cost = float(price) * 0.12
        ordering_cost = float(price) * 0.04
        if carrying_cost == 0:
            economic_order_quantity = np.nan
        else:
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost) / carrying_cost))

        annual_carrying_cost = economic_order_quantity / 2 * carrying_cost
        annual_ordering_cost = year_demand / economic_order_quantity * ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        length_of_order_cycle_days = economic_order_quantity / year_demand * 365
        number_cycles_per_year = 365 / length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(price)
        annual_investment_cost = number_cycles_per_year * investment_cost_per_cycle
        annual_total_cost = annual_investment_cost + annual_inventory_mgt_cost
        percentage_annual_inventory_mgt_cost_per_demand_cost = annual_inventory_mgt_cost / (annual_total_cost / 100)
        adjusted_length_of_supply_cycle = 7
        adjusted_quantity_per_week_cycle = (economic_order_quantity / length_of_order_cycle_days) * \
                                           adjusted_length_of_supply_cycle
        adjusted_annual_carrying_cost = (adjusted_quantity_per_week_cycle / 2) * carrying_cost
        adjusted_annual_ordering_cost = (year_demand / adjusted_quantity_per_week_cycle) * ordering_cost
        adjusted_annual_inventory_mgt_cost = adjusted_annual_carrying_cost + adjusted_annual_ordering_cost
        adjusted_investment_cost_per_cycle = adjusted_quantity_per_week_cycle * price
        adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost = adjusted_annual_inventory_mgt_cost / \
                                                                        (annual_investment_cost / 100)
        net_effect_on_inventory_mgt_costs = adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost - \
                                            percentage_annual_inventory_mgt_cost_per_demand_cost
        if stat == "adjusted_quantity_per_week_cycle":
            value = adjusted_quantity_per_week_cycle
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "adjusted_annual_carrying_cost":
            value = adjusted_annual_carrying_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "adjusted_annual_ordering_cost":
            value = adjusted_annual_ordering_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "adjusted_annual_inventory_mgt_cost":
            value = adjusted_annual_inventory_mgt_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "adjusted_investment_cost_per_cycle":
            value = adjusted_investment_cost_per_cycle
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost":
            value = adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        elif stat == "net_effect_on_inventory_mgt_costs":
            value = net_effect_on_inventory_mgt_costs
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
        else:
            value = adjusted_quantity_per_week_cycle
            return dict([('code', code), ('description', desc), ('ven', ven),("PRICE",price),
                         ("current_stock",current_stock), ('stat', value)])
