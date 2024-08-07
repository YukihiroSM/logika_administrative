import logging
from logika_statistics.models import Group
import time


def run():
    logger = logging.getLogger(__name__)
    all_groups = Group.objects.order_by("pk")
    print("Total groups:", len(all_groups))
    total = 0
    start_time = time.time()
    for i, group in enumerate(all_groups):
        lms_id = group.lms_id
        duplicates = Group.objects.filter(lms_id=lms_id)
        # print(f"{i} {group.pk} Group: {lms_id} ({group.status}). Duplicates amount: {len(duplicates)}")
        total += len(duplicates) - 1
        if len(duplicates) > 1:
            for d in duplicates:
                print(f"{group.pk} Group {group.lms_id}. ", end='')
                if d.status in ["20", "10"]:
                    main_group_pk = d.pk
                    duplicates = duplicates.exclude(pk=main_group_pk)
                    length = len(duplicates)
                    duplicates.delete()
                    # print(f"{length} duplicates has been deleted")
                    break
            else:
                print(f"{len(duplicates)} founded, but not deleted (not normal status)")

    print("Total duplicates", total)
    print("New total of groups", len(Group.objects.all()))
    print("Total time", (time.time() - start_time) / 60)
