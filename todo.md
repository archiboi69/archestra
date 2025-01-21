# Archestra TODOs

## Site Search

### Road Access
- [ ] Implement indirect road access analysis:
  - Calculate distance to nearest road plot for sites without direct access
  - Determine appropriate frontage calculation method for indirect access:
    1. Project site onto road plot boundary
    2. Use standard minimum frontage width (e.g., 4m)
    3. Calculate based on potential access path width
  - Add configurable maximum distance threshold for indirect access

### Data Management
- [ ] Consider implementing a more sophisticated data filtering system:
  - Make filtering thresholds configurable
  - Add additional filtering criteria based on:
    - Land use/zoning
    - Environmental constraints
    - Existing development density
  - Create a separate table for excluded plots with reason for exclusion
  - Add ability to "restore" filtered plots if needed
  - Consider implementing a staging table for new data imports