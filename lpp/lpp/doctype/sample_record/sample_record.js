// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Record", {
    refresh(frm) {
        if (frm.is_new()) {
            frm.events.set_table_parameters(frm);
        }

        // Update setup and production hours
        updateTotalHours(frm, 'start_date_setup_sample', 'end_date_setup_sample', 'total_hours_setup_sample');
        updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');

        // Update scrap, units per hour, and yields
        updateScrap(frm);
        updateUnitsPerHour(frm);
        calculateYield(frm, 'yield_sample', 'output_sample', 'input_sample');
        calculateYieldWithSetup(frm);
    },
    customer: function(frm) {
        if (frm.doc.customer) {
            fetchCustomerItems(frm);
        } else {
            clearCustomerItemSelection(frm);
        }
    },
    item_code: function(frm) {
        if (frm.doc.item_code) {
            fetchFilteredWorkOrders(frm);
        } else {
            frm.set_value('work_order', null);
            clearValuesIfNoWorkOrderOrJobCards(frm);
        }
    },
    set_table_parameters: function (frm) {
        const set_parameters = [
            { sample_parameters: 'Planned Date' },
            { sample_parameters: 'Actual Date' }
        ];

        frm.clear_table('sample_parameters');
        set_parameters.forEach(data => frm.add_child('sample_parameters', data));
        frm.refresh_field('sample_parameters');
    },
    start_date_setup_sample: updateSetupHours,
    end_date_setup_sample: updateSetupHours,
    start_date_production_sample: updateProductionHours,
    end_date_production_sample: updateProductionHours,
    setup_weight_setup_sample: function(frm) {
        calculateWeightOrUnit(frm, 'setup_weight_setup_sample', 'setup_quantity_setup_sample', true);
    },
    setup_quantity_setup_sample: function(frm) {
        calculateWeightOrUnit(frm, 'setup_quantity_setup_sample', 'setup_weight_setup_sample', false);
        calculateYieldWithSetup(frm);
    },
    setup_weight_production_sample: function(frm) {
        calculateWeightOrUnit(frm, 'setup_weight_production_sample', 'setup_quantity_production_sample', true);
    },
    setup_quantity_production_sample: function(frm) {
        calculateWeightOrUnit(frm, 'setup_quantity_production_sample', 'setup_weight_production_sample', false);
        calculateYieldWithSetup(frm);
    },
    input_sample: function(frm) {
        updateScrap(frm);
        calculateYieldWithSetup(frm);
    },
    output_sample: function(frm) {
        updateScrap(frm);
        calculateYieldWithSetup(frm);
    },
    work_order: function(frm) {
        fetchJobCardsForWorkOrder(frm);
    },
});

frappe.ui.form.on('Sample Parameters', {
    mold_creation: (frm, cdt, cdn) => updateStatus(frm, "mold_creation_status", "mold_creation"),
    sample_production: (frm, cdt, cdn) => updateStatus(frm, "sample_production_status", "sample_production"),
    customer_delivery: (frm, cdt, cdn) => updateStatus(frm, "customer_delivery_status", "customer_delivery")
});

function fetchCustomerItems(frm) {
    frappe.call({
        method: "lpp.lpp.doctype.sample_record.sample_record.get_customer_items",
        args: { customer_name: frm.doc.customer },
        callback: function(response) {
            const items = response.message || [];
            frm.set_query('item_code', () => ({ filters: [['Item', 'name', 'in', items]] }));
            if (!items.includes(frm.doc.item_code)) {
                frm.set_value({ 'item_code': null, 'item_name': null });
            }
        }
    });
}

function clearCustomerItemSelection(frm) {
    frm.set_value({ 'item_code': null, 'item_name': null, 'work_order': null });
    frm.set_query('item_code', () => ({}));
}

function updateStatus(frm, targetField, dateField) {
    const { sample_parameters } = frm.doc;
    const plannedDate = sample_parameters.find(row => row.sample_parameters === "Planned Date")?.[dateField];
    const actualDate = sample_parameters.find(row => row.sample_parameters === "Actual Date")?.[dateField];

    frm.set_value(targetField, plannedDate && actualDate ? 
        new Date(actualDate) > new Date(plannedDate) ? 'Late' : 'Ontime' : null
    );
}

function updateTotalHours(frm, startField, endField, outputField) {
    const startDate = frm.doc[startField], endDate = frm.doc[endField];    
    frm.set_value(outputField, startDate && endDate ? 
        ((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60)).toFixed(2) : null
    );
}

function calculateWeightOrUnit(frm, sourceField, targetField, isUnitToWeight) {    
    if (frm.doc.weight__unit && frm.doc[sourceField]) {
        const calculatedValue = isUnitToWeight ?
            frm.doc[sourceField] / frm.doc.weight__unit :
            frm.doc[sourceField] * frm.doc.weight__unit;
        if (frm.doc[targetField] !== calculatedValue) {
            frm.set_value(targetField, calculatedValue);
        }
    }
}

function updateUnitsPerHour(frm) {    
    frm.set_value('units__hour_sample', 
        frm.doc.output_sample && frm.doc.total_hours_production_sample 
            ? parseInt(frm.doc.total_hours_production_sample, 10) === 0 
                ? null 
                : frm.doc.output_sample / frm.doc.total_hours_production_sample
            : null
    );
}

function updateScrap(frm) {
    frm.set_value('scrap_sample', 
        !isNaN(frm.doc.input_sample) && !isNaN(frm.doc.output_sample) 
            ? frm.doc.input_sample - frm.doc.output_sample 
            : null
    );
}

function calculateYield(frm, outputField, outputValueField, inputValueField) {
    frm.set_value(outputField, 
        frm.doc[outputValueField] && frm.doc[inputValueField] 
            ? (frm.doc[outputValueField] / frm.doc[inputValueField]) * 100 
            : null
    );
}

function calculateYieldWithSetup(frm) {
    if (frm.doc.input_sample && frm.doc.output_sample && frm.doc.setup_weight_setup_sample && frm.doc.setup_weight_production_sample) {
        const totalWeight = Number(frm.doc.setup_weight_setup_sample) + Number(frm.doc.setup_weight_production_sample);
        frm.set_value('yield_with_setup_sample', (frm.doc.output_sample / (frm.doc.input_sample + totalWeight)) * 100);
    }
}

// Helper functions for triggers
function updateSetupHours(frm) {
    updateTotalHours(frm, 'start_date_setup_sample', 'end_date_setup_sample', 'total_hours_setup_sample');
}

function updateProductionHours(frm) {
    updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');
    updateUnitsPerHour(frm);
}

function fetchFilteredWorkOrders(frm) {
    if (frm.doc.item_code && frm.doc.customer) {
        frappe.call({
            method: "lpp.lpp.doctype.sample_record.sample_record.get_filtered_work_orders",
            args: {
                item_code: frm.doc.item_code,
                customer_name: frm.doc.customer
            },
            callback: function(response) {
                const work_orders = response.message || [];
                
                // Set filter on work_order field and clear invalid selection if necessary
                frm.set_query('work_order', () => ({ filters: [['Work Order', 'name', 'in', work_orders]] }));
                clearInvalidWorkOrder(frm, work_orders);
            }
        });
    } else {
        // Reset work_order and remove filters if item_code or customer is missing
        frm.set_value('work_order', null);
        frm.set_query('work_order', () => ({}));
    }
}

function clearInvalidWorkOrder(frm, validWorkOrders) {
    if (frm.doc.work_order && !validWorkOrders.includes(frm.doc.work_order)) {
        frm.set_value('work_order', null);
    }
}

function fetchJobCardsForWorkOrder(frm) {
    if (frm.doc.work_order) {
        frappe.call({
            method: "lpp.lpp.doctype.sample_record.sample_record.get_job_cards_for_work_order",
            args: {
                work_order: frm.doc.work_order
            },
            callback: async function(response) {
                const { job_cards: jobCards = [], scrap_items: scrapItems = [] } = response.message || {};
                
                // เคลียร์ค่าหากไม่มี Job Cards
                if (!jobCards.length) {
                    clearValuesIfNoWorkOrderOrJobCards(frm);
                    return;
                }
                
                const firstJobCard = jobCards[0];
                const lastJobCard = jobCards[jobCards.length - 1];

                // ตั้งค่าเริ่มต้นจาก Job Card
                if (firstJobCard) {
                    frm.set_value({
                        'start_date_setup': firstJobCard.custom_start_date_setup || null,
                        'start_date_production': firstJobCard.custom_start_date_production || null,
                    });
                }

                if (lastJobCard) {
                    frm.set_value({
                        'end_date_setup': lastJobCard.custom_end_date_setup || null,
                        'end_date_production': lastJobCard.custom_end_date_production || null
                    });

                    // คำนวณชั่วโมงรวม
                    if (firstJobCard) {
                        frm.set_value({
                            'total_hours_setup': calculateHoursDifference(firstJobCard.custom_start_date_setup, lastJobCard.custom_end_date_setup),
                            'total_hours_production': calculateHoursDifference(firstJobCard.custom_start_date_production, lastJobCard.custom_end_date_production)
                        });
                    }
                }

                // คำนวณค่าเฉลี่ยและค่าต่าง ๆ
                const avgUnitQuantitySetup = calculateAverage(jobCards, 'custom_as_unit_quantity_setup');
                const avgWeightSetup = calculateAverage(jobCards, 'custom_as_weight_setup');
                const avgUnitQuantityProduction = calculateAverage(jobCards, 'custom_as_unit_quantity_production');
                const avgWeightProduction = calculateAverage(jobCards, 'custom_as_weight_production');
                const avgInputProduction = calculateAverage(jobCards, 'custom_input_production');
                const avgOutputProduction = calculateAverage(jobCards, 'custom_output_production');
                
                const scrap = avgInputProduction - avgOutputProduction || 0; // Default to 0 if undefined
                const hoursDifference = calculateHoursDifference(firstJobCard.custom_start_date_production, lastJobCard.custom_end_date_production) || 1; // Prevent division by zero
                
                // ตั้งค่าผลลัพธ์ในฟอร์ม
                frm.set_value({
                    'setup_weight_setup': avgUnitQuantitySetup || null,
                    'setup_quantity_setup': avgWeightSetup || null,
                    'setup_weight_production': avgUnitQuantityProduction || null,
                    'setup_quantity_production': avgWeightProduction || null,
                    'input': avgInputProduction || null,
                    'output': avgOutputProduction || null,
                    'scrap': scrap,
                    'units__hour': parseInt(hoursDifference) === 0 ? null : (avgOutputProduction / hoursDifference).toFixed(2),
                    'yield': avgInputProduction ? ((avgOutputProduction / avgInputProduction) * 100).toFixed(2) : null,
                    'yield_with_setup': parseInt(avgInputProduction + avgWeightSetup + avgWeightProduction) === 0
                        ? null
                        : ((avgOutputProduction / (avgInputProduction + avgWeightSetup + avgWeightProduction)) * 100).toFixed(2),
                });
                
                if(scrapItems){
                    frm.clear_table('scrap_items');
                    scrapItems.forEach(data => frm.add_child('scrap_items', data));
                    frm.refresh_field('scrap_items');
                }
            }
        });
    } else {
        clearValuesIfNoWorkOrderOrJobCards(frm);
    }
}

function calculateHoursDifference(startDate, endDate) {
    return ((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60)).toFixed(2);
}

function calculateAverage(jobCards, fieldName) {
    if (!jobCards || jobCards.length === 0) return 0;

    const total = jobCards.reduce((sum, jobCard) => sum + (jobCard[fieldName] || 0), 0);
    return (total / jobCards.length).toFixed(2);
}

function clearValuesIfNoWorkOrderOrJobCards(frm,) {
    frm.set_value({
        'start_date_setup': null,
        'start_date_production': null,
        'end_date_setup': null,
        'end_date_production': null,
        'total_hours_setup': null,
        'total_hours_production': null,
        'setup_weight_setup': null,
        'setup_quantity_setup': null,
        'setup_weight_production': null,
        'setup_quantity_production': null,
        'input': null,
        'output': null,
        'scrap': null,
        'units__hour': null,
        'yield': null,
        'yield_with_setup': null
    });
}