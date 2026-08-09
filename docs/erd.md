---
title: "Email: Database Diagrams"
description: "Auto-generated ER diagrams for the Email module."
sidebar:
  badge:
    text: "Auto-gen"
    variant: "note"
---

:::caution[Auto-generated]
These diagrams are auto-generated from Django model introspection.
Do not edit. Run `make erd` in entirius-docker to regenerate.
:::

## Channel Configuration

```d2 layout=elk
Channel: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  idx: varchar
  "label": varchar
  from_name: varchar
  from_email: varchar
  from_t9n: jsonb
  main_background_color: varchar
  body_background_color: varchar
}

LangChannelConfig: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language: varchar
  shop_name: varchar
  logo_url: varchar
  header_mail: varchar
  footer_copy: text
  footer_name_brand: varchar
}



LangChannelConfig.channel_id -> Channel.id: {style.stroke: "#00ACC1"}
```

## Email Templates

```d2 layout=elk
AccountsNewAccount: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  announce: text
  confirm_button: text
  thank_you: text
}

AccountsResetPassword: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  reset_button: text
  help: text
}

CheckoutVirtualProduct: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  order: text
  products: text
  key_name: varchar
}

LoyaltyCouponConfirmation: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  thank_you: text
  coupon_copy: text
  coupon_button: text
}

ReturnsReturnConfirmation: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  return_copy: text
  comment_copy: text
  print_copy: text
}

AllegroVirtualProduct: {
  shape: sql_table
  style.fill: "#00ACC1"
  style.stroke: "#12141A"
  style.font-color: "#EBEDF2"
  id: int {constraint: primary_key}
  channel_id: int {constraint: foreign_key}
  language_id: int {constraint: foreign_key}
  subject: varchar
  welcome: text
  order: text
  products: text
  key_name: varchar
}

Channel: {
  shape: sql_table
  style.fill: "#484B57"
  style.stroke: "#1A1C25"
  style.stroke-dash: 3
  style.font-color: "#9A9CAA"
  id: int {constraint: primary_key}
  label: "Channel (See channel-config diagram)"
}

Language: {
  shape: sql_table
  style.fill: "#484B57"
  style.stroke: "#1A1C25"
  style.stroke-dash: 3
  style.font-color: "#9A9CAA"
  id: int {constraint: primary_key}
  label: "Language (External: django_regional)"
}



AccountsNewAccount.channel_id -> Channel.id: {style.stroke: "#484B57"}

AccountsNewAccount.language_id -> Language.id: {style.stroke: "#484B57"}

AccountsResetPassword.channel_id -> Channel.id: {style.stroke: "#484B57"}

AccountsResetPassword.language_id -> Language.id: {style.stroke: "#484B57"}

CheckoutVirtualProduct.channel_id -> Channel.id: {style.stroke: "#484B57"}

CheckoutVirtualProduct.language_id -> Language.id: {style.stroke: "#484B57"}

LoyaltyCouponConfirmation.channel_id -> Channel.id: {style.stroke: "#484B57"}

LoyaltyCouponConfirmation.language_id -> Language.id: {style.stroke: "#484B57"}

ReturnsReturnConfirmation.channel_id -> Channel.id: {style.stroke: "#484B57"}

ReturnsReturnConfirmation.language_id -> Language.id: {style.stroke: "#484B57"}

AllegroVirtualProduct.channel_id -> Channel.id: {style.stroke: "#484B57"}

AllegroVirtualProduct.language_id -> Language.id: {style.stroke: "#484B57"}
```
