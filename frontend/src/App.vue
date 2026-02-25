<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
:root {
  /* ── Design System Tokens ── */
  --color-primary: #6C5CE7;
  --color-primary-dark: #5A4BD1;
  --color-primary-light: #A29BFE;
  --color-primary-bg: #F0EEFF;
  --color-secondary: #00B894;
  --color-secondary-dark: #00A381;
  --color-accent: #FD79A8;
  --color-warning: #FDCB6E;
  --color-danger: #FF6B6B;
  --color-success: #00B894;
  --color-info: #74B9FF;
  --color-text: #1A1A2E;
  --color-text-secondary: #4A4A68;
  --color-text-muted: #9494AB;
  --color-bg: #F5F6FA;
  --color-surface: #FFFFFF;
  --color-border: #EDEDF3;
  --color-sidebar: #1A1A2E;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;

  /* ── Shadows ── */
  --shadow-xs: 0 1px 2px rgba(108, 92, 231, 0.04);
  --shadow-sm: 0 1px 3px rgba(108, 92, 231, 0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(108, 92, 231, 0.08), 0 2px 4px rgba(0,0,0,0.04);
  --shadow-lg: 0 8px 32px rgba(108, 92, 231, 0.12), 0 4px 8px rgba(0,0,0,0.06);
  --shadow-xl: 0 16px 48px rgba(108, 92, 231, 0.16);

  /* ── Radii ── */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* ── Gradients ── */
  --gradient-primary: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
  --gradient-hero: linear-gradient(135deg, #6C5CE7 0%, #8B7CF7 50%, #A29BFE 100%);
  --gradient-success: linear-gradient(135deg, #00B894 0%, #55E6C1 100%);
  --gradient-warm: linear-gradient(135deg, #FD79A8 0%, #FDCB6E 100%);
  --gradient-blue: linear-gradient(135deg, #74B9FF 0%, #A29BFE 100%);
  --gradient-surface: linear-gradient(180deg, #FFFFFF 0%, #FAFBFE 100%);

  /* ── Element Plus Theme Override ── */
  --el-color-primary: #6C5CE7;
  --el-color-primary-light-3: #9B8FEF;
  --el-color-primary-light-5: #B5ADF3;
  --el-color-primary-light-7: #D0CBF7;
  --el-color-primary-light-8: #DDD9F9;
  --el-color-primary-light-9: #EDEAFC;
  --el-color-primary-dark-2: #5A4BD1;
  --el-color-success: #00B894;
  --el-color-success-light-3: #4DD9AC;
  --el-color-success-light-5: #7FE6C5;
  --el-color-success-light-7: #B2F0DD;
  --el-color-success-light-8: #CCF5E9;
  --el-color-success-light-9: #E6FAF4;
  --el-color-success-dark-2: #00A381;
  --el-color-warning: #FDCB6E;
  --el-color-danger: #FF6B6B;
  --el-border-radius-base: 8px;
  --el-font-family: var(--font-sans);
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── Global Scrollbar ── */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #d0d0d8;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #b0b0bc;
}

/* ── Element Plus Global Refinements ── */
.el-card {
  --el-card-border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.el-card__header {
  font-weight: 600;
  font-size: 15px;
  color: var(--color-text);
  padding: 16px 20px;
}

.el-table {
  --el-table-border-color: var(--color-border);
  --el-table-header-bg-color: #FAFAFD;
  --el-table-row-hover-bg-color: #F8F7FE;
  font-size: 14px;
}

.el-table th.el-table__cell {
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.el-dialog {
  --el-dialog-border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
}

.el-dialog__header {
  padding: 20px 24px 16px;
}

.el-dialog__title {
  font-weight: 700;
  font-size: 17px;
  color: var(--color-text);
}

.el-dialog__body {
  padding: 8px 24px 24px;
}

.el-button {
  font-weight: 500;
}

.el-button--primary {
  box-shadow: 0 2px 8px rgba(108, 92, 231, 0.25);
}

.el-button--primary:hover {
  box-shadow: 0 4px 12px rgba(108, 92, 231, 0.35);
}

.el-tag {
  font-weight: 500;
}
</style>
