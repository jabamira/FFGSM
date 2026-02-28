# Custom UI Component Library

This is a custom, lightweight component library for the Fuel & Lubricants Accounting System built with **Vue 3** and **Tailwind CSS**. It eliminates the need for third-party UI libraries like Flowbite while maintaining full customization and control.

## Components Included

### 1. **Button**

Versatile button component with multiple variants and sizes.

**Props:**

- `variant` - `'primary' | 'secondary' | 'danger' | 'success' | 'outline' | 'ghost'` (default: `'primary'`)
- `size` - `'xs' | 'sm' | 'md' | 'lg' | 'xl'` (default: `'md'`)
- `label` - Button text
- `disabled` - Disable button
- `loading` - Show loading spinner
- `fullWidth` - Make button 100% width
- `rounded` - Fully rounded button

**Example:**

```vue
<Button variant="primary" size="lg" label="Save Changes" @click="handleSave" />
```

---

### 2. **TextInput**

Text input field with validation support.

**Props:**

- `modelValue` - v-model binding
- `type` - Input type (`'text' | 'email' | 'password' | 'number' | 'date'`)
- `label` - Field label
- `placeholder` - Placeholder text
- `error` - Error message to display
- `hint` - Helper text
- `disabled` - Disable input
- `required` - Mark as required
- `id` - Input ID

**Example:**

```vue
<TextInput
  v-model="email"
  type="email"
  label="Email Address"
  placeholder="user@example.com"
  error="Invalid email"
  required
/>
```

---

### 3. **SelectInput**

Dropdown select component.

**Props:**

- `modelValue` - v-model binding
- `options` - Array of `{ value: string, label: string }`
- `label` - Field label
- `placeholder` - Placeholder text
- `error` - Error message
- `hint` - Helper text
- `disabled` - Disable select
- `required` - Mark as required
- `id` - Select ID

**Example:**

```vue
<SelectInput
  v-model="productType"
  label="Product Type"
  :options="[
    { value: 'oil', label: 'Motor Oil' },
    { value: 'coolant', label: 'Engine Coolant' },
  ]"
  placeholder="Select a product"
/>
```

---

### 4. **DataTable**

Powerful data table with sorting, pagination, and row selection.

**Props:**

- `data` - Array of row objects (required)
- `columns` - Array of `{ key: string, label: string, type?: string }`
- `actions` - Array of action buttons
- `selectable` - Enable row selection
- `paginate` - Enable pagination
- `pageSize` - Rows per page (default: 10)

**Column Types:**

- `'string'` - Default text
- `'date'` - Formatted date
- `'currency'` - Formatted currency
- `'percent'` - Percentage format

**Example:**

```vue
<DataTable
  :data="products"
  :columns="[
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Product Name' },
    { key: 'price', label: 'Price', type: 'currency' },
    { key: 'date', label: 'Date Added', type: 'date' },
  ]"
  :actions="[
    { name: 'edit', label: 'Edit', event: 'edit-row' },
    { name: 'delete', label: 'Delete', event: 'delete-row' },
  ]"
  selectable
  paginate
  page-size="10"
  @edit-row="editProduct"
  @delete-row="deleteProduct"
/>
```

---

### 5. **Modal**

Reusable modal/dialog component.

**Props:**

- `isOpen` - Controls modal visibility
- `title` - Modal title
- `confirmLabel` - Confirm button text
- `hideConfirm` - Hide confirm button

**Slots:**

- `default` - Modal body content
- `footer` - Custom footer content

**Example:**

```vue
<Modal
  :is-open="showModal"
  title="Confirm Action"
  confirm-label="Delete"
  @close="showModal = false"
  @confirm="handleDelete"
>
  <p>Are you sure you want to delete this item?</p>
</Modal>
```

---

### 6. **Alert**

Dismissible alert/notification component.

**Props:**

- `type` - `'success' | 'error' | 'warning' | 'info'` (default: `'info'`)
- `title` - Alert title
- `message` - Alert message (required)
- `closeable` - Show close button
- `icon` - Show icon

**Example:**

```vue
<Alert
  type="success"
  title="Saved!"
  message="Your changes have been saved successfully."
/>
```

---

### 7. **Badge**

Tag/badge component for status labels.

**Props:**

- `type` - `'default' | 'success' | 'error' | 'warning' | 'info' | 'primary'`
- `size` - `'sm' | 'md' | 'lg'`
- `label` - Badge text
- `outline` - Outline style instead of filled

**Example:**

```vue
<Badge type="success" label="Active" />
<Badge type="warning" label="Pending" outline />
```

---

## Theme Configuration

All components use a centralized theme configuration located in `src/components/ui/theme.js`. Customize colors, sizes, and styles globally:

```javascript
export const theme = {
  colors: {
    primary: "blue",
    danger: "red",
    // ...
  },
  button: {
    sizes: {
      /* ... */
    },
    variants: {
      /* ... */
    },
  },
  // ...
};
```

---

## Installation & Usage

### 1. Import Components

```javascript
import { Button, TextInput, DataTable, Modal } from "@/components/ui";
```

### 2. Use in Template

```vue
<template>
  <div>
    <Button variant="primary" label="Submit" @click="handleSubmit" />
    <TextInput v-model="name" label="Name" />
    <DataTable :data="items" :columns="columns" />
  </div>
</template>
```

### 3. Register Globally (Optional)

In `src/main.js`:

```javascript
import {
  Button,
  TextInput,
  DataTable,
  Modal,
  Alert,
  Badge,
  SelectInput,
} from "@/components/ui";

app.component("Button", Button);
app.component("TextInput", TextInput);
// Register other components...
```

---

## Component Showcase

Visit the **Component Showcase** page to see all components in action:

```
http://localhost:5173/#/components
```

This page demonstrates:

- All button variants and sizes
- Form inputs with validation
- Alert types
- Badge styles
- Data table with pagination
- Modal interactions
- Code examples

---

## Customization

### Tailwind CSS Integration

All components use Tailwind utility classes. The project is configured with Tailwind CSS 4.x. Customize by:

1. **Modifying `theme.js`** for global color/size changes
2. **Editing component files** for specific styling
3. **Updating `tailwind.config.js`** for project-wide settings

### Example: Change Primary Color

Edit `src/components/ui/theme.js`:

```javascript
button: {
  variants: {
    primary: {
      base: 'bg-purple-600 hover:bg-purple-700 text-white', // Changed from blue
      disabled: 'bg-purple-300 text-gray-100',
    },
    // ...
  },
}
```

---

## Best Practices

1. **Use v-model for forms** - TextInput and SelectInput support two-way binding
2. **Leverage slots** - Modal, DataTable, and Badge support slots for flexibility
3. **Handle events** - Use @click, @edit-row, @delete-row for user interactions
4. **Validate early** - Use `error` prop to show validation messages
5. **Keep it simple** - Components are lightweight; compose them for complex UIs

---

## Performance

- **No external dependencies** - Only Vue 3 and Tailwind CSS
- **Tree-shakeable** - Import only what you use
- **Small bundle size** - ~15KB minified (all components)
- **Fast rendering** - Vue 3 composition API optimizations

---

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE 11+ with polyfills

---

## Future Enhancements

Potential additions to the component library:

- [ ] Checkbox component
- [ ] Radio button component
- [ ] File upload component
- [ ] Date picker component
- [ ] Multi-select dropdown
- [ ] Toast notifications
- [ ] Stepper component
- [ ] Accordion component
- [ ] Tabs component
- [ ] Search/autocomplete

---

## License

Part of the Fuel & Lubricants Accounting System project.
