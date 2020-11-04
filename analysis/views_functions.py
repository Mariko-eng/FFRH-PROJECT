import pandas as pd
import numpy as np
import math
from scipy.stats import t


def calc_stats(product):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    if arr != []:
        p_sum = data_np_arr.sum()
        p_mean = data_np_arr.mean()
        p_min = data_np_arr.min()
        p_max = data_np_arr.max()
        p_length = len(data_np_arr)
        x2 = []
        x_vbar = []
        x_vbar3 = []
        x_vbar4 = []
        for value in data_np_arr:
            x2.append(pow(value, 2))
            val = value - p_mean
            x_vbar.append(val)
            x_vbar3.append(pow(val, 3))
            x_vbar4.append(pow(val, 4))

        x2_np_arr = np.array(x2)
        x_vbar3_arr = np.array(x_vbar3)
        x_vbar4_arr = np.array(x_vbar4)
        x2_sum = x2_np_arr.sum()
        square_of_sum = pow(p_sum, 2)
        square_n = square_of_sum / (p_length)
        if p_length == 1 or p_length == 0:
            var = np.nan
            std = np.nan
            std_error = np.nan
            skewness = np.nan
            kurtosis = np.nan
        else:
            var = ((x2_sum) - (square_n)) / (p_length - 1)
            std = np.sqrt(var)
            std_error = np.float(std) / np.sqrt(p_length)
            ns3 = p_length * pow(std, 3)
            ns4 = p_length * pow(std, 4)
            if ns3 != 0:
                skewness = float(x_vbar3_arr.sum()) / float(ns3)
                a = x_vbar4_arr.sum()
                b = float(a)
                kurtosis = ((b) / float(ns4)) - 3
            else:
                skewness = np.nan
                kurtosis = np.nan

        q1, q2, q3 = np.percentile(data_np_arr.astype(int), [25, 50, 75])
        iqr = q3 - q1
        qty_mild_outlier_lt = q1 - (1.5 * iqr)
        qty_mild_outlier_gt = q3 + (1.5 * iqr)
        extreme_value_lt = q1 - (3 * iqr)
        extreme_value_gt = q3 + (3 * iqr)

        return dict([('months_of_stock', p_length), ('qty_sum', p_sum), ('qty_mean', p_mean),
                     ('qty_min', p_min), ('qty_median', q2), ('qty_max', p_max), ('qty_std', std),
                     ('qty_var', var), ('qty_std_error', std_error), ('qty_skew', skewness),
                     ('qty_kurt', kurtosis), ('qty_q1', q1), ('qty_q2', q2), ('qty_q3', q3),
                     ('qty_iqr', iqr), ('qty_mild_outlier_lt', qty_mild_outlier_lt),
                     ('qty_mild_outlier_gt', qty_mild_outlier_gt), ('extreme_value_lt', extreme_value_lt),
                     ('extreme_value_gt', extreme_value_gt)])
    else:
        return dict([('months_of_stock', None), ('qty_sum', None), ('qty_mean', None),
                     ('qty_min', None), ('qty_median', None), ('qty_max', None), ('qty_std', None),
                     ('qty_var', None), ('qty_std_error', None), ('qty_skew', None),
                     ('qty_kurt', None), ('qty_q1', None), ('qty_q2', None), ('qty_q3', None),
                     ('qty_iqr', None), ('qty_mild_outlier_lt', None),
                     ('qty_mild_outlier_gt', None), ('extreme_value_lt', None),
                     ('extreme_value_gt', None)])


def consumption_method_1_month_cycle(product):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    price = float(product.price)
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
        percentage_change_in_consumption = deviation_from_mean
        min_amc = amc_in_packs*((100 - percentage_change_in_consumption)/100)
        max_amc = amc_in_packs*((100 + percentage_change_in_consumption)/100)
        poisson_mode_quantity = round(amc_in_packs)
        poisson_mode_qty_adjusted_for_changes_in_use = poisson_mode_quantity
        safety_stock = poisson_mode_qty_adjusted_for_changes_in_use * 0.5
        qty_to_procure = poisson_mode_qty_adjusted_for_changes_in_use * (0.5+1) + safety_stock
        eff_qty_to_procure =qty_to_procure
        calc_1_month_cycle_qty_to_procure_adjusted_for_losses = eff_qty_to_procure
        calculated_1_month_cycle_cost_of_procurement = price * calc_1_month_cycle_qty_to_procure_adjusted_for_losses
        calculated_1_month_cycle_cost_of_procurement_thousand = calculated_1_month_cycle_cost_of_procurement/1000
        consumption_annual_procurement_cost = 12 * calculated_1_month_cycle_cost_of_procurement
        budget_deficit_in_plan = calculated_1_month_cycle_cost_of_procurement - float(planned_qty_1_month_order_cost)
        if calculated_1_month_cycle_cost_of_procurement != 0:
            percentage_available_funding = float(planned_qty_1_month_order_cost) / (
                    calculated_1_month_cycle_cost_of_procurement / 100)
        else:
            percentage_available_funding = np.nan
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean',planned_qty_1_month_mean),
                     ('planned_qty_1_month_order_cost',planned_qty_1_month_order_cost),
                     ('planned_qty_1_month_order_cost_thousands',planned_qty_1_month_order_cost_thousands),
                     ('annual_plan_cost',annual_plan_cost),
                     ('amc_in_packs', np.round(amc_in_packs,2)),
                     ('amc_adjusted_for_stock_outs',np.round(amc_adjusted_for_stock_outs,2)),
                     ('percentage_change_in_consumption', np.round(percentage_change_in_consumption,2)),
                     ('min_amc',np.round(min_amc,2)),
                     ('max_amc',np.round(max_amc,2)),
                     ('poisson_mode_quantity',poisson_mode_quantity),
                     ('safety_stock',safety_stock),
                     ('qty_to_procure',qty_to_procure),
                     ('calculated_1_month_cycle_cost_of_procurement',calculated_1_month_cycle_cost_of_procurement),
                     ('calculated_1_month_cycle_cost_of_procurement_thousand',
                      calculated_1_month_cycle_cost_of_procurement_thousand),
                     ('consumption_annual_procurement_cost',consumption_annual_procurement_cost),
                     ('budget_deficit_in_plan',budget_deficit_in_plan),
                     ('percentage_available_funding',np.round(percentage_available_funding,2))])
    else:
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean', planned_qty_1_month_mean),
                     ('planned_qty_1_month_order_cost', planned_qty_1_month_order_cost),
                     ('planned_qty_1_month_order_cost_thousands', planned_qty_1_month_order_cost_thousands),
                     ('annual_plan_cost', annual_plan_cost),
                     ('amc_in_packs', None),
                     ('amc_adjusted_for_stock_outs', None),
                     ('percentage_change_in_consumption', None),
                     ('min_amc', None),
                     ('max_amc', None),
                     ('poisson_mode_quantity', None),
                     ('safety_stock', None),
                     ('qty_to_procure', None),
                     ('calculated_1_month_cycle_cost_of_procurement', None),
                     ('calculated_1_month_cycle_cost_of_procurement_thousand',None),
                     ('consumption_annual_procurement_cost', None),
                     ('budget_deficit_in_plan', None),
                     ('percentage_available_funding', None)])


def eoq_model_1_month_cycle(product):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    price = product.price
    planned_qty_2_month_mean = product.planned_Qty_2Month_Mean
    planned_qty_1_month_mean = planned_qty_2_month_mean / 2
    planned_qty_1_month_order_cost = price * planned_qty_1_month_mean
    planned_qty_1_month_order_cost_thousands = planned_qty_1_month_order_cost / 1000
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
        percentage_annual_inventory_mgt_cost_per_demand_cost = annual_inventory_mgt_cost/(annual_total_cost/100)
        plan_budget_deficit = float(annual_plan_cost) - float(annual_investment_cost)
        percentage_available_funding = float(annual_plan_cost) / (float(annual_investment_cost) / 100)
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean',planned_qty_1_month_mean),
                     ('planned_qty_1_month_order_cost',planned_qty_1_month_order_cost),
                     ('planned_qty_1_month_order_cost_thousands',planned_qty_1_month_order_cost_thousands),
                     ('year_demand',year_demand),('carrying_cost',carrying_cost),
                     ('ordering_cost',ordering_cost),('economic_order_quantity',np.round(economic_order_quantity,2)),
                     ('annual_carrying_cost',np.round(annual_carrying_cost,2)),
                     ('annual_ordering_cost', np.round(annual_ordering_cost,2)),
                     ('annual_inventory_mgt_cost',np.round(annual_inventory_mgt_cost,2)),
                     ('annual_demand_cost', annual_demand_cost),
                     ('length_of_order_cycle_days',np.round(length_of_order_cycle_days,2)),
                     ('number_cycles_per_year',np.round(number_cycles_per_year,2)),
                     ('investment_cost_per_cycle',np.round(investment_cost_per_cycle,2)),
                     ('annual_investment_cost',np.round(annual_investment_cost,2)),
                     ('annual_investment_cost_millions',np.round(annual_investment_cost_millions,2)),
                     ('annual_total_cost',np.round(annual_total_cost,2)),
                     ('annual_total_cost_millions',
                      np.round(annual_total_cost_millions,2)),
                     ('percentage_annual_inventory_mgt_cost_per_demand_cost',
                      np.round(percentage_annual_inventory_mgt_cost_per_demand_cost,2)),
                     ('plan_budget_deficit',np.round(plan_budget_deficit,2)),
                     ('percentage_available_funding',np.round(percentage_available_funding,2))])
    else:
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean',planned_qty_1_month_mean),
                     ('planned_qty_1_month_order_cost',planned_qty_1_month_order_cost),
                     ('planned_qty_1_month_order_cost_thousands',planned_qty_1_month_order_cost_thousands),
                     ('year_demand', None), ('carrying_cost', None),
                     ('ordering_cost', None), ('economic_order_quantity', None),
                     ('annual_carrying_cost',None),
                     ('annual_ordering_cost', None),
                     ('annual_inventory_mgt_cost',None),
                     ('annual_demand_cost', None),
                     ('length_of_order_cycle_days',None),
                     ('number_cycles_per_year',None),
                     ('investment_cost_per_cycle',None),
                     ('annual_investment_cost',None),
                     ('annual_investment_cost_millions',None),
                     ('annual_total_cost',None),
                     ('annual_total_cost_millions',None),
                     ('percentage_annual_inventory_mgt_cost_per_demand_cost',None),
                     ('plan_budget_deficit',None),
                     ('percentage_available_funding',None)])


def standardised_consumption_plan_1_week_cycle(product):
    product_data = product.consumptiondata_set.all()
    arr = []
    for p in product_data:
        if p.consumptionQty != None:
            arr.append(p.consumptionQty)

    data_np_arr = np.array(arr)
    code = product.code
    desc = product.description
    price = float(product.price)
    planned_qty_2_month_mean = product.planned_Qty_2Month_Mean
    planned_qty_1_month_mean = planned_qty_2_month_mean / 2
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
        adjusted_quantity_per_week_cycle = (economic_order_quantity/length_of_order_cycle_days) * 7
        adjusted_length_of_supply_cycle = 7
        adjusted_annual_carrying_cost = (adjusted_quantity_per_week_cycle/2) * carrying_cost
        adjusted_annual_ordering_cost = (year_demand/adjusted_quantity_per_week_cycle) * ordering_cost
        adjusted_annual_inventory_mgt_cost = adjusted_annual_carrying_cost + adjusted_annual_ordering_cost
        adjusted_investment_cost_per_cycle = adjusted_quantity_per_week_cycle * price
        adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost = adjusted_annual_inventory_mgt_cost / \
                                                                        (annual_investment_cost/100)
        net_effect_on_inventory_mgt_costs = adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost -\
                                            percentage_annual_inventory_mgt_cost_per_demand_cost
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean',planned_qty_1_month_mean),
                     ('amc_in_packs', np.round(amc_in_packs,2)),
                     ('adjusted_quantity_per_week_cycle',np.round(adjusted_quantity_per_week_cycle,2)),
                     ('adjusted_annual_carrying_cost',np.round(adjusted_annual_carrying_cost,2)),
                     ('adjusted_annual_ordering_cost',np.round(adjusted_annual_ordering_cost,2)),
                     ('adjusted_annual_inventory_mgt_cost',
                      np.round(adjusted_annual_inventory_mgt_cost,2)),
                     ('adjusted_investment_cost_per_cycle',np.round(adjusted_investment_cost_per_cycle,2)),
                     ('adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost',
                      np.round(adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost,2)),
                     ('net_effect_on_inventory_mgt_costs',np.round(net_effect_on_inventory_mgt_costs,2))])
    else:
        return dict([('code', code), ('desc', desc),('price',price),
                     ('planned_qty_1_month_mean',planned_qty_1_month_mean),
                     ('amc_in_packs', None),
                     ('adjusted_quantity_per_week_cycle',None),
                     ('adjusted_annual_carrying_cost',None),
                     ('adjusted_annual_ordering_cost',None),
                     ('adjusted_annual_inventory_mgt_cost',
                      None),
                     ('adjusted_investment_cost_per_cycle',None),
                     ('adjusted_percentage_annual_inventory_mgt_cost_per_demand_cost',
                      None),
                     ('net_effect_on_inventory_mgt_costs',None)])

