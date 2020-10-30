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


def consumption_method_2_month_cycle(product):
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
        #print(product.description)
        code = product.code
        desc = product.description
        plannedQty2Month_order_cost = product.price * product.planned_Qty_2Month_Mean
        planned_Qty_Month_Mean = product.planned_Qty_2Month_Mean / 2
        plannedQtyMonth_order_cost = product.price * planned_Qty_Month_Mean
        annualplancost = plannedQtyMonth_order_cost * 12
        percentage_change_in_consumption = deviation_from_mean
        amc_in_packs = float(p_mean)
        no_of_stockouts = 0
        amc_adjusted_for_stockouts = amc_in_packs / (1 - (no_of_stockouts / 30.5))
        amc_adjusted_for_changes = amc_adjusted_for_stockouts * (1 + (percentage_change_in_consumption / 100))
        safety_stock = amc_adjusted_for_changes * 1
        qty_to_procure = amc_adjusted_for_changes * (1 + 2) + safety_stock
        calculated_2Month_qty_to_procure = qty_to_procure
        calculated_2Month_cost_of_procurement = calculated_2Month_qty_to_procure * float(product.price)
        budget_deficit_in_plan = calculated_2Month_cost_of_procurement - float(plannedQty2Month_order_cost)
        if calculated_2Month_cost_of_procurement != 0:
            percentage_available_funding = float(plannedQty2Month_order_cost) / (
                calculated_2Month_cost_of_procurement / 100)
        else:
            percentage_available_funding = np.nan

        return dict([('code',code),('desc',desc),
                     ('planned_Qty_Month_Mean', planned_Qty_Month_Mean),
                     ('plannedQty2Month_order_cost', plannedQty2Month_order_cost),
                     ('annualplancost', annualplancost),
                     ('amc_in_packs', amc_in_packs),
                     ('amc_adjusted_for_stockouts', amc_adjusted_for_stockouts),
                     ('percentage_change_in_consumption', percentage_change_in_consumption),
                     ('amc_adjusted_for_changes', amc_adjusted_for_changes),
                     ('safety_stock', safety_stock),
                     ('calculated_2Month_qty_to_procure', calculated_2Month_qty_to_procure),
                     ('calculated_2Month_cost_of_procurement', calculated_2Month_cost_of_procurement),
                     ('budget_deficit_in_plan', budget_deficit_in_plan),
                     ('percentage_available_funding', percentage_available_funding)])
    else:
        return dict([('code',None),('desc',None),
                     ('planned_Qty_Month_Mean', None),
                     ('plannedQty2Month_order_cost', None),
                     ('annualplancost', None),
                     ('amc_in_packs', None),
                     ('amc_adjusted_for_stockouts', None),
                     ('percentage_change_in_consumption', None),
                     ('amc_adjusted_for_changes', None),
                     ('safety_stock', None),
                     ('calculated_2Month_qty_to_procure', None),
                     ('calculated_2Month_cost_of_procurement', None),
                     ('budget_deficit_in_plan', None),
                     ('percentage_available_funding', None)])


def consumption_method_3_month_cycle(product):
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
        code =product.code
        desc = product.description
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
        budget_deficit_in_plan = calculated_3_month_cycle_cost_of_procurement - float(planned_qty_3_month_order_cost)
        if calculated_3_month_cycle_cost_of_procurement !=0:
            percentage_available_funding = float(planned_qty_3_month_order_cost) / (
                calculated_3_month_cycle_cost_of_procurement / 100)
        else:
            percentage_available_funding = np.nan

        return dict([('code',code),('desc',desc),
                     ('planned_qty_3_month_mean', planned_qty_3_month_mean),
                     ('planned_qty_3_month_order_cost', planned_qty_3_month_order_cost),
                     ('annual_plan_cost', annual_plan_cost),
                     ('amc_in_packs', amc_in_packs),
                     ('amc_adjusted_for_stock_outs', amc_adjusted_for_stock_outs),
                     ('percentage_change_in_consumption', percentage_change_in_consumption),
                     ('amc_adjusted_for_changes', amc_adjusted_for_changes),
                     ('safety_stock', safety_stock),
                     ('calculated_3_month_qty_to_procure', calculated_3_month_qty_to_procure),
                     ('calculated_3_month_cycle_cost_of_procurement', calculated_3_month_cycle_cost_of_procurement),
                     ('budget_deficit_in_plan', budget_deficit_in_plan),
                     ('percentage_available_funding', percentage_available_funding)])
    else:
        return dict([('code',None),('desc',None),
                     ('planned_qty_3_month_mean', None),
                     ('planned_qty_3_month_order_cost', None),
                     ('annual_plan_cost', None),
                     ('amc_in_packs', None),
                     ('amc_adjusted_for_stock_outs', None),
                     ('percentage_change_in_consumption', None),
                     ('amc_adjusted_for_changes', None),
                     ('safety_stock', None),
                     ('calculated_3_month_qty_to_procure', None),
                     ('calculated_3_month_cycle_cost_of_procurement', None),
                     ('budget_deficit_in_plan', None),
                     ('percentage_available_funding', None)])


def eoq_model_2_month_cycle(product):
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
        planned_Qty_Month_Mean = product.planned_Qty_2Month_Mean / 2
        plannedQtyMonth_order_cost = product.price * planned_Qty_Month_Mean
        annual_plan_cost = plannedQtyMonth_order_cost * 12
        percentage_change_in_consumption = deviation_from_mean
        amc_in_packs = float(p_mean)
        no_of_stockouts = 0
        amc_adjusted_for_stockouts = amc_in_packs / (1 - (no_of_stockouts / 30.5))
        amc_adjusted_for_changes = amc_adjusted_for_stockouts * (1 + (percentage_change_in_consumption / 100))

        year_demand = amc_adjusted_for_changes *12
        carrying_cost = float(product.price) * 0.12
        ordering_cost = float(product.price) * 0.04

        if carrying_cost == 0:
            economic_order_quantity = np.nan
        else:
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost)/carrying_cost))

        #economic_order_quantity = np.sqrt(2*year_demand*ordering_cost/carrying_cost)
        annual_carrying_cost = economic_order_quantity/2*carrying_cost
        annual_ordering_cost = year_demand/economic_order_quantity*ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        annual_demand_cost = year_demand * float(product.price)
        length_of_order_cycle_days = economic_order_quantity/year_demand*365
        number_cycles_per_year = 365/length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(product.price)
        investment_cost_per_year = investment_cost_per_cycle * number_cycles_per_year
        annual_total_cost = investment_cost_per_year + annual_inventory_mgt_cost
        percentage_inventory_mgt_cost = annual_inventory_mgt_cost/(annual_total_cost/100)
        plan_budget_deficit = annual_total_cost - float(annual_plan_cost)
        percentage_available__funding = float(annual_plan_cost) / (annual_total_cost/100)

        return dict([('code',code),('desc',desc),
                     ('amc_in_packs', amc_in_packs),
                     ('yearly_demand', year_demand),
                     ('carrying_cost', carrying_cost),
                     ('ordering_cost', ordering_cost),
                     ('economic_order_quantity', economic_order_quantity),
                     ('annual_carrying_cost', annual_carrying_cost),
                     ('annual_ordering_cost', annual_ordering_cost),
                     ('annual_inventory_mgt_cost', annual_inventory_mgt_cost),
                     ('annual_demand_cost', annual_demand_cost),
                     ('length_of_order_cycle_days', length_of_order_cycle_days),
                     ('number_cycles_per_year', number_cycles_per_year),
                     ('investment_cost_per_cycle', investment_cost_per_cycle),
                     ('investment_cost_per_year', investment_cost_per_year),
                     ('annual_total_cost', annual_total_cost),
                     ('percentage_inventory_mgt_cost', percentage_inventory_mgt_cost),
                     ('plan_budget_deficit', plan_budget_deficit),
                     ('percentage_available__funding', percentage_available__funding)])
    else:
        return dict([('code',None),('desc',None),
                     ('amc_in_packs', None),
                     ('yearly_demand', None),
                     ('carrying_cost', None),
                     ('ordering_cost', None),
                     ('economic_order_quantity', None),
                     ('annual_carrying_cost', None),
                     ('annual_ordering_cost', None),
                     ('annual_inventory_mgt_cost', None),
                     ('annual_demand_cost', None),
                     ('length_of_order_cycle_days', None),
                     ('number_cycles_per_year', None),
                     ('investment_cost_per_cycle', None),
                     ('investment_cost_per_year', None),
                     ('annual_total_cost', None),
                     ('percentage_inventory_mgt_cost', None),
                     ('plan_budget_deficit', None),
                     ('percentage_available__funding', None)])


def eoq_model_3_month_cycle(product):
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
        planned_qty_month_mean = product.planned_Qty_2Month_Mean / 2
        planned_qty_3_month_mean = planned_qty_month_mean * 3
        planned_qty_3_month_order_cost = float(planned_qty_3_month_mean) * float(product.price)
        annual_plan_cost = planned_qty_3_month_order_cost * 4
        amc_in_packs = float(p_mean)
        no_of_stock_outs = 0
        amc_adjusted_for_stock_outs = amc_in_packs / (1 - (no_of_stock_outs / 30.5))
        #amc_adjusted_for_stock_outs = amc_in_packs
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
            economic_order_quantity = np.sqrt(((2 * year_demand * ordering_cost)/carrying_cost))

        annual_carrying_cost = economic_order_quantity/2*carrying_cost
        annual_ordering_cost = year_demand/economic_order_quantity*ordering_cost
        annual_inventory_mgt_cost = annual_carrying_cost + annual_ordering_cost
        annual_demand_cost = year_demand * float(product.price)
        length_of_order_cycle_days = economic_order_quantity/year_demand*365
        number_cycles_per_year = 365 / length_of_order_cycle_days
        investment_cost_per_cycle = economic_order_quantity * float(product.price)
        investment_cost_per_year = investment_cost_per_cycle * number_cycles_per_year
        annual_total_cost = investment_cost_per_year + annual_inventory_mgt_cost
        percentage_inventory_mgt_cost = annual_inventory_mgt_cost/(annual_total_cost/100)
        plan_budget_deficit = annual_total_cost - float(annual_plan_cost)
        percentage_available__funding = float(annual_plan_cost) / (annual_total_cost/100)

        return dict([('code',code),('desc',desc),
                     ('amc_in_packs',amc_in_packs),
                     ('yearly_demand', year_demand),
                     ('carrying_cost', carrying_cost),
                     ('ordering_cost', ordering_cost),
                     ('economic_order_quantity', economic_order_quantity),
                     ('annual_carrying_cost', annual_carrying_cost),
                     ('annual_ordering_cost', annual_ordering_cost),
                     ('annual_inventory_mgt_cost', annual_inventory_mgt_cost),
                     ('annual_demand_cost', annual_demand_cost),
                     ('length_of_order_cycle_days', length_of_order_cycle_days),
                     ('number_cycles_per_year', number_cycles_per_year),
                     ('investment_cost_per_cycle', investment_cost_per_cycle),
                     ('investment_cost_per_year', investment_cost_per_year),
                     ('annual_total_cost', annual_total_cost),
                     ('percentage_inventory_mgt_cost', percentage_inventory_mgt_cost),
                     ('plan_budget_deficit', plan_budget_deficit),
                     ('percentage_available__funding', percentage_available__funding)])
    else:
        return dict([('code',None),('desc',None),
                     ('amc_in_packs', None),
                     ('yearly_demand', None),
                     ('carrying_cost', None),
                     ('ordering_cost', None),
                     ('economic_order_quantity', None),
                     ('annual_carrying_cost', None),
                     ('annual_ordering_cost', None),
                     ('annual_inventory_mgt_cost', None),
                     ('annual_demand_cost', None),
                     ('length_of_order_cycle_days', None),
                     ('number_cycles_per_year', None),
                     ('investment_cost_per_cycle', None),
                     ('investment_cost_per_year', None),
                     ('annual_total_cost', None),
                     ('percentage_inventory_mgt_cost', None),
                     ('plan_budget_deficit', None),
                     ('percentage_available__funding', None)])