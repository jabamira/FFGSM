# Field Validation & Error Handling Implementation Guide

## Overview

This guide documents the field validation and error handling system implemented for the Fire Station application. The system provides:

1. **Field Requirements Display**: Shows constraints from backend models (max length, required fields, etc.)
2. **Error Modal**: Displays validation and API errors in a professional modal window
3. **Field Hints**: Helps users understand field requirements while filling forms
4. **Centralized Error Handling**: Replaces browser alerts with proper error UI

---

## Architecture

### 1. Field Definitions (`src/config/fieldDefinitions.js`)

Contains metadata for all form fields extracted from Django models:

```javascript
export const fieldDefinitions = {
  user: {
    name: {
      label: "Имя",
      required: true,
      maxLength: 40,
      hint: "До 40 символов",
    },
    // ... more fields
  },
  role: {
    // ...
  },
  passengerCar: {
    // ...
  },
  // ... more entities
};
```

**Available entities:** `user`, `role`, `passengerCar`, `fireTruck`, `normsPassengerCars`, `normsFireTrucks`, `waybillRecord`

**Field properties:**

- `label`: Display name for the field
- `required`: Whether field is mandatory
- `maxLength`: Maximum characters (for text)
- `minLength`: Minimum characters (for passwords)
- `minValue`/`maxValue`: For numeric fields
- `maxDigits`/`decimalPlaces`: For decimal fields
- `unique`: Whether value must be unique
- `type`: Field type ('decimal', 'integer', 'time', etc.)
- `hint`: Help text shown to user

### 2. Error Modal Component (`src/components/ErrorModal.vue`)

Displays API errors and validation errors in a user-friendly modal.

**Features:**

- Parses Django REST Framework error responses
- Shows field-specific errors
- Professional styling with color-coded sections
- Automatically extracts error details from `error.response.data`

**Usage in components:**

```vue
<template>
  <ErrorModal ref="errorModalRef" />
  <!-- form content -->
</template>

<script setup>
import { ref } from "vue";
import ErrorModal from "./ErrorModal.vue";

const errorModalRef = ref(null);

const handleSubmit = async () => {
  try {
    // API call
    await axios.post("/endpoint", data);
  } catch (error) {
    errorModalRef.value?.openModal(error);
  }
};
</script>
```

### 3. Form Composable (`src/composables/useFormSubmit.js`)

Provides unified error and success handling for forms.

---

## Implemented Examples

### ✅ Components Updated:

- `UserEditModal.vue` - Edit user modal
- `RoleEditModal.vue` - Edit role modal
- `ErrorModal.vue` - Centralized error display
- `fieldDefinitions.js` - Field metadata

### ✅ Views Updated:

- `Users.vue` - Add/list users with validation
- `Roles.vue` - Add/list roles with validation
- `FireTrucksList.vue` - Add/edit fire trucks with validation

---

## Pattern for Updating Forms

### Step 1: Import Required Components & Config

```javascript
import { ref } from "vue";
import {
  Modal,
  Button,
  TextInput,
  SelectInput,
} from "../components/ui/importUi";
import ErrorModal from "../components/ErrorModal.vue";
import { fieldDefinitions } from "../config/fieldDefinitions";
import axios from "axios";
import { useAuthStore } from "../stores/auth";
```

### Step 2: Setup Refs

```javascript
const auth = useAuthStore();
const errorModalRef = ref(null);
const showModal = ref(false);
const formData = ref({
  // your fields
});
```

### Step 3: Add ErrorModal to Template

```vue
<template>
  <ErrorModal ref="errorModalRef" />

  <Modal :is-open="showModal">
    <!-- form fields -->
  </Modal>
</template>
```

### Step 4: Use Field Definitions in Form Fields

```vue
<TextInput
  v-model="formData.fieldName"
  :label="fieldDefinitions.entityType.fieldName.label"
  :hint="fieldDefinitions.entityType.fieldName.hint"
  :required="fieldDefinitions.entityType.fieldName.required"
  placeholder="Enter value"
/>
```

### Step 5: Update Submit Handler

```javascript
const submitForm = async () => {
  // Basic validation
  if (!formData.value.requiredField) {
    const error = new Error("Validation Error");
    error.response = {
      data: {
        detail: "Please fill required fields",
        requiredField: "This field is required",
      },
    };
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    const response = await axios.post("/endpoint", formData.value, {
      headers: { Authorization: `Bearer ${auth.access}` },
    });
    // Handle success
    closeModal();
  } catch (error) {
    // Show error modal instead of alert
    errorModalRef.value?.openModal(error);
  }
};
```

---

## Adding New Field Definitions

When adding forms for new entities:

1. **Check Django Models** for constraints:
   - `CharField(max_length=N)` → `maxLength: N`
   - `DecimalField(max_digits=X, decimal_places=Y)` → `maxDigits: X, decimalPlaces: Y`
   - `PositiveIntegerField(validators=[MaxValueValidator(N)])` → `maxValue: N`
   - `BooleanField(default=False)` → already a checkbox
   - `unique=True` → `unique: true`
   - `blank=False` or `null=False` → `required: true`

2. **Update `fieldDefinitions.js`**:

```javascript
export const fieldDefinitions = {
  newEntity: {
    fieldName: {
      label: "Display Name",
      required: true,
      maxLength: 100,
      hint: "Up to 100 characters",
    },
    // ... more fields
  },
  // ... keep existing entities
};
```

3. **Add Helper Functions** if needed:

```javascript
export function getFieldDefinition(entityType, fieldName) {
  return fieldDefinitions[entityType]?.[fieldName] || null;
}

export function getFieldHint(entityType, fieldName) {
  return getFieldDefinition(entityType, fieldName)?.hint || "";
}
```

---

## Remaining Work

### Views Needing Updates:

- [ ] `LightVehiclesList.vue` - Passenger cars
- [ ] `FireTrucksNorms.vue` - Fire truck norms
- [ ] `LightVehiclesNorms.vue` - Passenger car norms
- [ ] `FireTrucksWayBills.vue` - Fire truck waybills
- [ ] `LightVehiclesWayBills.vue` - Passenger car waybills
- [ ] `FuelReport.vue` - Fuel reports
- [ ] `Drivers.vue` - Driver information

### Field Definitions Still Needed:

- Driver fields (if applicable)
- Report-specific fields
- Any custom validation rules

### Enhancement Ideas:

1. **Field-level Error Display**: Show errors under individual fields
   - Add `error` prop to `TextInput` and `SelectInput` components
   - Display specific field errors from API response

2. **Success Notifications**: Show "Saved successfully" messages
   - Create `useNotifications` composable
   - Display toast messages after successful operations

3. **Loading States**: Disable buttons while submitting
   - Add `isLoading` state to forms
   - Show loading spinner on submit button

4. **Optimistic Updates**: Update UI before server confirmation
   - Update local state immediately
   - Revert if server error occurs

---

## Best Practices

### ✅ DO:

- Always import and use `fieldDefinitions` for consistency
- Use `ErrorModal` for all error scenarios
- Validate required fields before submission
- Show hints to help users understand requirements
- Parse all error responses through `ErrorModal`

### ❌ DON'T:

- Use browser `alert()` for errors
- Hardcode field labels in templates
- Mix validation logic with UI
- Ignore backend error responses
- Use different error handling patterns in different views

---

## Example: Complete Form Implementation

```vue
<template>
  <ErrorModal ref="errorModalRef" />

  <Modal :is-open="isOpen" @close="closeModal">
    <div class="space-y-4">
      <TextInput
        v-model="form.name"
        :label="fieldDefinitions.user.name.label"
        :hint="fieldDefinitions.user.name.hint"
        :required="fieldDefinitions.user.name.required"
      />
      <TextInput
        v-model="form.login"
        :label="fieldDefinitions.user.login.label"
        :hint="fieldDefinitions.user.login.hint"
        :required="fieldDefinitions.user.login.required"
      />
      <SelectInput
        v-model="form.role"
        :label="fieldDefinitions.user.role.label"
        :hint="fieldDefinitions.user.role.hint"
        :options="roleOptions"
      />
    </div>

    <template #footer>
      <Button @click="closeModal">Cancel</Button>
      <Button @click="submit" variant="primary">Save</Button>
    </template>
  </Modal>
</template>

<script setup>
import { ref } from "vue";
import {
  Modal,
  Button,
  TextInput,
  SelectInput,
} from "../components/ui/importUi";
import ErrorModal from "../components/ErrorModal.vue";
import { fieldDefinitions } from "../config/fieldDefinitions";
import { useAuthStore } from "../stores/auth";
import axios from "axios";

const auth = useAuthStore();
const errorModalRef = ref(null);
const isOpen = ref(false);
const form = ref({
  name: "",
  login: "",
  role: null,
});

const submit = async () => {
  // Validation
  if (!form.value.name || !form.value.login) {
    const error = new Error("Validation Error");
    error.response = {
      data: {
        detail: "Fill all required fields",
        name: !form.value.name ? "Required" : null,
        login: !form.value.login ? "Required" : null,
      },
    };
    errorModalRef.value?.openModal(error);
    return;
  }

  try {
    await axios.post("/users/", form.value, {
      headers: { Authorization: `Bearer ${auth.access}` },
    });
    closeModal();
  } catch (error) {
    errorModalRef.value?.openModal(error);
  }
};

const closeModal = () => {
  isOpen.value = false;
};
</script>
```

---

## Testing Checklist

For each form you update:

- [ ] Field labels display correctly
- [ ] Hints show under fields
- [ ] Required fields show asterisk (\*)
- [ ] Validation runs before submission
- [ ] Empty required fields show error modal
- [ ] API error responses show in error modal
- [ ] Field-specific errors display with field names
- [ ] Error modal closes properly
- [ ] Form data persists through validation errors
- [ ] Success closes form/resets data
- [ ] Works on mobile screen sizes

---

## References

### Related Files:

- [`src/config/fieldDefinitions.js`](../../src/config/fieldDefinitions.js)
- [`src/components/ErrorModal.vue`](../../src/components/ErrorModal.vue)
- [`src/components/ui/TextInput.vue`](../../src/components/ui/TextInput.vue)
- [`src/components/ui/SelectInput.vue`](../../src/components/ui/SelectInput.vue)
- [`src/composables/useFormSubmit.js`](../../src/composables/useFormSubmit.js)

### Django Models Reference:

- `serverFireStation/fire_station_project/fuel/models.py`

---

## Support

For questions or issues with this implementation:

1. Check this guide for examples
2. Review implemented examples (Users.vue, Roles.vue)
3. Ensure field definitions match Django model constraints
4. Verify error response format from API
