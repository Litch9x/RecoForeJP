package com.recoforejp.itemservice.item;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.recoforejp.itemservice.catalog.Category;
import com.recoforejp.itemservice.catalog.CategoryRepository;
import com.recoforejp.itemservice.catalog.Tag;
import com.recoforejp.itemservice.catalog.TagRepository;
import com.recoforejp.itemservice.item.dto.CreateItemRequest;
import com.recoforejp.itemservice.item.dto.UpdateItemRequest;
import java.util.HashMap;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ItemServiceTest {

  @Mock ItemRepository itemRepository;
  @Mock CategoryRepository categoryRepository;
  @Mock TagRepository tagRepository;
  @InjectMocks ItemService itemService;

  private Category jobCategory() {
    return Category.builder().id(1).slug("job").nameJa("就職").build();
  }

  @Test
  void create_resolvesCategoryAndTagsAndSaves() {
    when(categoryRepository.findBySlug("job")).thenReturn(Optional.of(jobCategory()));
    when(tagRepository.findByName("english-ok"))
        .thenReturn(Optional.of(Tag.builder().id(10).name("english-ok").build()));
    when(itemRepository.save(any(Item.class))).thenAnswer(inv -> inv.getArgument(0));

    CreateItemRequest req =
        CreateItemRequest.builder()
            .categorySlug("job")
            .title("Test item")
            .tags(Set.of("english-ok"))
            .languages(Set.of("ja", "en"))
            .metadata(new HashMap<>())
            .build();

    Item saved = itemService.create(req);

    assertThat(saved.getCategory().getSlug()).isEqualTo("job");
    assertThat(saved.getTags()).extracting(Tag::getName).containsExactly("english-ok");
    assertThat(saved.getLanguages()).containsExactlyInAnyOrder("ja", "en");
    verify(itemRepository).save(any(Item.class));
  }

  @Test
  void create_throwsWhenCategoryUnknown() {
    when(categoryRepository.findBySlug("nope")).thenReturn(Optional.empty());

    CreateItemRequest req =
        CreateItemRequest.builder()
            .categorySlug("nope")
            .title("x")
            .metadata(new HashMap<>())
            .build();

    assertThatThrownBy(() -> itemService.create(req))
        .isInstanceOf(InvalidReferenceException.class)
        .hasMessageContaining("Unknown category slug");
    verify(itemRepository, never()).save(any());
  }

  @Test
  void create_throwsWhenTagUnknown() {
    when(categoryRepository.findBySlug("job")).thenReturn(Optional.of(jobCategory()));
    when(tagRepository.findByName("bad-tag")).thenReturn(Optional.empty());

    CreateItemRequest req =
        CreateItemRequest.builder()
            .categorySlug("job")
            .title("x")
            .tags(Set.of("bad-tag"))
            .metadata(new HashMap<>())
            .build();

    assertThatThrownBy(() -> itemService.create(req))
        .isInstanceOf(InvalidReferenceException.class)
        .hasMessageContaining("bad-tag");
  }

  @Test
  void get_throws404WhenMissing() {
    UUID id = UUID.randomUUID();
    when(itemRepository.findById(id)).thenReturn(Optional.empty());
    assertThatThrownBy(() -> itemService.get(id)).isInstanceOf(ItemNotFoundException.class);
  }

  @Test
  void update_partialKeepsExistingValuesForNullFields() {
    UUID id = UUID.randomUUID();
    Item existing =
        Item.builder()
            .category(jobCategory())
            .title("Old title")
            .description("Old desc")
            .metadata(new HashMap<>())
            .build();
    existing.setId(id);
    when(itemRepository.findById(id)).thenReturn(Optional.of(existing));
    when(itemRepository.save(any(Item.class))).thenAnswer(inv -> inv.getArgument(0));

    UpdateItemRequest req = UpdateItemRequest.builder().title("New title").build();

    Item updated = itemService.update(id, req);

    assertThat(updated.getTitle()).isEqualTo("New title");
    assertThat(updated.getDescription()).isEqualTo("Old desc"); // preserved
  }

  @Test
  void delete_throwsWhenMissing() {
    UUID id = UUID.randomUUID();
    when(itemRepository.existsById(id)).thenReturn(false);
    assertThatThrownBy(() -> itemService.delete(id)).isInstanceOf(ItemNotFoundException.class);
    verify(itemRepository, never()).deleteById(any());
  }

  @Test
  void delete_callsRepositoryWhenExists() {
    UUID id = UUID.randomUUID();
    when(itemRepository.existsById(id)).thenReturn(true);
    itemService.delete(id);
    verify(itemRepository).deleteById(id);
  }
}
