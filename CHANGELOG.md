# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-09-22

### Added
- Created `template-twitter-card.xml` with initial fixes for Twitter Card meta data.

### Changed
- **Improved Performance:**
    - Replaced an inefficient, script-based related posts feature with a faster, server-side implementation using Blogger's built-in data tags.
    - Removed an unnecessary external JavaScript library (`lazysizes.min.js`) in favor of modern browsers' native `loading="lazy"` attribute.
- **Improved Accessibility:**
    - Refactored the search `<label>` to a semantic `<button>` for better screen reader support.
- **Improved Maintainability:**
    - Replaced hardcoded blog titles, author names, and the copyright year with dynamic Blogger data tags and scripts.
    - Removed several unused and non-functional widgets (`HTML3`, `LinkList2`, `Image2`) to clean up the template.
