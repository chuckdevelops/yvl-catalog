import React, { useState } from "react";
import { cn } from "../../lib/utils";
import { Card, CardHeader, CardContent } from "./card";
import { Input } from "./input";
import { Button } from "./button";

const FilterSelect = React.forwardRef(
  ({ id, label, options, value, className, onChange, ...props }, ref) => {
    return (
      <div className="mb-3">
        <label htmlFor={id} className="form-label">{label}</label>
        <select 
          id={id}
          name={id}
          className={cn("form-select", className)}
          value={value}
          onChange={onChange}
          ref={ref}
          {...props}
        >
          <option value="">All {label}s</option>
          {options.map((option, index) => (
            <option key={index} value={option.value || option}>
              {option.label || option}
            </option>
          ))}
        </select>
      </div>
    );
  }
);
FilterSelect.displayName = "FilterSelect";

const FilterForm = React.forwardRef(
  ({ 
    className,
    action,
    filters = [],
    initialValues = {},
    showClearButton = true,
    clearUrl = "",
    submitText = "Apply Filters",
    clearText = "Clear Filters",
    ...props 
  }, ref) => {
    const [values, setValues] = useState(initialValues);
    
    const handleChange = (e) => {
      const { name, value } = e.target;
      setValues({
        ...values,
        [name]: value
      });
    };
    
    const hasFilters = Object.values(values).some(value => !!value);
    
    return (
      <Card className={cn("filter-form", className)} ref={ref} {...props}>
        <CardHeader>
          <h3>Filters</h3>
        </CardHeader>
        <CardContent>
          <form method="get" action={action} className="row">
            {filters.map((filter, index) => (
              <div className="col-md-3" key={index}>
                {filter.type === 'select' ? (
                  <FilterSelect
                    id={filter.id}
                    label={filter.label}
                    options={filter.options}
                    value={values[filter.id] || ''}
                    onChange={handleChange}
                  />
                ) : filter.type === 'search' ? (
                  <div className="mb-3">
                    <label htmlFor={filter.id} className="form-label">{filter.label}</label>
                    <Input
                      type="text"
                      id={filter.id}
                      name={filter.id}
                      placeholder={filter.placeholder || `Search ${filter.label.toLowerCase()}...`}
                      value={values[filter.id] || ''}
                      onChange={handleChange}
                    />
                  </div>
                ) : null}
              </div>
            ))}
            
            <div className="col-md-12">
              <Button type="submit" className="me-2">{submitText}</Button>
              {showClearButton && hasFilters && (
                <Button variant="outline" as="a" href={clearUrl}>{clearText}</Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    );
  }
);
FilterForm.displayName = "FilterForm";

export { FilterForm };