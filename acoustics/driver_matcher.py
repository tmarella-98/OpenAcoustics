from dataclasses import dataclass

import matplotlib.pyplot as plt

from acoustics.driver import Driver
from acoustics.requirements import Requirements


@dataclass
class MatchResult:
    driver: Driver
    overall_score: float
    parameter_scores: dict[str, float]
    notes: list[str]

    def summary(self) -> None:
        print("=" * 50)
        print(f"{self.driver.manufacturer} {self.driver.model}")
        print("=" * 50)
        print(f"Overall match: {self.overall_score:.1f}%")
        print()

        print("Parameter scores")
        print("-" * 40)
        for parameter, score in self.parameter_scores.items():
            print(f"{parameter:20s}: {score:.1f}%")

        print()
        print("Notes")
        print("-" * 40)
        for note in self.notes:
            print(note)

    def plot_scores(self) -> None:
        parameters = list(self.parameter_scores.keys())
        scores = list(self.parameter_scores.values())

        plt.figure(figsize=(9, 4))
        plt.bar(parameters, scores)
        plt.ylim(0, 100)
        plt.ylabel("Match score (%)")
        plt.title(f"{self.driver.manufacturer} {self.driver.model} - T/S Match")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.show()


class DriverMatcher:
    """Scores how well a driver satisfies project requirements."""

    def match(self, driver: Driver, requirements: Requirements) -> MatchResult:
        parameter_scores = {}
        notes = []

        if requirements.target_f3_hz is not None:
            parameter_scores["Fs"] = self._score_maximum(driver.fs, requirements.target_f3_hz)
            parameter_scores["Qts"] = self._score_range(driver.qts, 0.25, 0.50)
            parameter_scores["Qes"] = self._score_range(driver.qes, 0.25, 0.60)
            parameter_scores["Vas"] = self._score_vas(driver.vas, requirements.max_box_volume_l)
            parameter_scores["Sd"] = self._score_minimum(driver.sd, 120.0)
            parameter_scores["Xmax"] = self._score_minimum(driver.xmax, 5.0)
            parameter_scores["BL"] = self._score_minimum(driver.bl, 6.0)

            if driver.fs <= requirements.target_f3_hz:
                notes.append("✓ Fs is suitable for the target bass extension.")
            else:
                notes.append("✗ Fs is higher than the target F3; bass extension may be limited.")

            if 0.25 <= driver.qts <= 0.50:
                notes.append("✓ Qts is in a useful range for sealed/vented hi-fi alignments.")
            else:
                notes.append("⚠ Qts is outside the initial preferred range.")

        if requirements.nominal_impedance_ohm is not None:
            parameter_scores["Re"] = self._score_impedance(
                re=driver.re,
                nominal_impedance=requirements.nominal_impedance_ohm,
            )

        if requirements.max_driver_diameter_mm is not None:
            estimated_diameter_mm = self._estimate_diameter_from_sd(driver.sd)
            parameter_scores["Diameter"] = self._score_maximum(
                estimated_diameter_mm,
                requirements.max_driver_diameter_mm,
            )

        if requirements.target_spl_db is not None:
            notes.append("⚠ SPL matching not implemented yet because Driver has no sensitivity field.")

        if requirements.max_thd_percent is not None:
            notes.append("⚠ THD matching not implemented yet because Driver has no distortion data.")

        if requirements.max_cost_usd is not None:
            notes.append("⚠ Cost matching not implemented yet because Driver has no cost field.")

        overall_score = (
            sum(parameter_scores.values()) / len(parameter_scores)
            if parameter_scores
            else 0.0
        )

        return MatchResult(
            driver=driver,
            overall_score=overall_score,
            parameter_scores=parameter_scores,
            notes=notes,
        )

    @staticmethod
    def _score_maximum(value: float, target: float) -> float:
        if value <= target:
            return 100.0

        score = 100.0 * target / value
        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_minimum(value: float, target: float) -> float:
        if value >= target:
            return 100.0

        score = 100.0 * value / target
        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_range(value: float, minimum: float, maximum: float) -> float:
        if minimum <= value <= maximum:
            return 100.0

        if value < minimum:
            score = 100.0 * value / minimum
        else:
            score = 100.0 * maximum / value

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_vas(vas_l: float, max_box_volume_l: float | None) -> float:
        if max_box_volume_l is None:
            return 100.0

        # Rough first-pass heuristic:
        # For compact boxes, lower Vas is easier to work with.
        preferred_vas = max_box_volume_l * 4.0

        if vas_l <= preferred_vas:
            return 100.0

        score = 100.0 * preferred_vas / vas_l
        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_impedance(re: float, nominal_impedance: float) -> float:
        ideal_re = nominal_impedance * 0.75
        error_ratio = abs(re - ideal_re) / ideal_re
        score = 100.0 * (1.0 - error_ratio)
        return max(0.0, min(100.0, score))

    @staticmethod
    def _estimate_diameter_from_sd(sd_cm2: float) -> float:
        sd_mm2 = sd_cm2 * 100.0
        radius_mm = (sd_mm2 / 3.141592653589793) ** 0.5
        return 2.0 * radius_mm