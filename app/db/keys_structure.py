db_table_partkey = 'partkey'
db_table_sortkey = 'sortkey'

user_partkey = 'user_'
user_sortkey = '{uuid}'
user_record_type = 'user_'

tg_user_partkey = 'tg_user'
tg_user_sortkey = '{tg_id}'
tg_user_record_type = 'tg_user'

token_partkey = '{jti}'
token_sortkey = 'token'

shop_partkey = 'shop'
shop_sortkey = '{shop_uuid}'
shop_record_type = 'shop'

template_partkey = 'template'
template_sortkey = '{uuid}'
template_record_type = 'template'

product_category_partkey = "product_category_{shop_uuid}"
product_category_sortkey = "{uuid}"
product_category_record_type = 'product_category'

product_base_partkey = "product_{shop_uuid}"
product_base_sortkey = "{product_uuid}"
product_base_record_type = 'product_base_info'

product_variant_partkey = "product_{shop_uuid}"
product_variant_sortkey = "{product_uuid}_variant_{variant_uuid}"
product_variant_record_type = 'product_variant'

product_extra_kits_partkey = "product_{shop_uuid}"
product_extra_kits_sortkey = "{product_uuid}_extra_kit_{extra_kit_uuid}"
product_extra_kits_record_type = 'product_extra_kits'

delivery_self_pickup_partkey = "delivery_{shop_uuid}"
delivery_self_pickup_sortkey = "self_pickup_{self_pickup_uuid}"
delivery_self_pickup_record_type = 'delivery_self_pickup'

delivery_manual_partkey = "delivery_{shop_uuid}"
delivery_manual_sortkey = "manual_{delivery_manual_uuid}"
delivery_manual_record_type = 'delivery_manual'

backup_url = '{owner_uuid}/backup-{datetime}.json'

infopages_rubrics_partkey = "infopages_rubric_{shop_uuid}"
infopages_rubrics_sortkey = "{rubric_uuid}"
infopages_rubrics_record_type = 'infopages_rubric'

infopages_posts_partkey = "infopages_posts_{shop_uuid}"
infopages_posts_sortkey = "{post_uuid}"
infopages_posts_record_type = 'infopages_posts'
