from newclid.auxiliary_constructions import insert_aux_to_premise


class TestAlphaGeometry:
    def test_insert_aux_to_premise(self):
        pstring = (
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b "
            "? perp a d b c"
        )
        auxstring = "e = on_line e a c, on_line e b d"

        target = (
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b; "
            "e = on_line e a c, on_line e b d "
            "? perp a d b c"
        )
        assert insert_aux_to_premise(pstring, auxstring) == target
