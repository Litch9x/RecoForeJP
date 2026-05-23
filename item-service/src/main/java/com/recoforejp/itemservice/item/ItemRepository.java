package com.recoforejp.itemservice.item;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ItemRepository extends JpaRepository<Item, UUID> {

  List<Item> findByCategoryId(Integer categoryId);

  List<Item> findByRegion(String region);
}
